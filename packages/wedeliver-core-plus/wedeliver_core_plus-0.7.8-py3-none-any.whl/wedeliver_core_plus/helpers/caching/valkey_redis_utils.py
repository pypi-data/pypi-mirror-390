import json
import hashlib
from datetime import timedelta
from redis import Redis, exceptions as redis_exceptions
from sqlalchemy import event, inspect
from flask import current_app


class BaseCacheRule:
    """
    Base caching rule that:
    - Uses a singleton Redis (Valkey) client
    - Reads config from Flask app
    - Supports multiple models + per-model events/columns
    - Invalidates cache when model events or watched columns change
    - Uses dynamic API path set by the route decorator
    - Supports granular invalidation via invalidation_key_fields
    - Supports field aliases for API param → DB column mapping

    invalidation_key_fields formats:
        - Empty list []: Path-based invalidation (invalidates all cache for endpoint)
        - String "field": Granular invalidation (same name in API and DB)
        - Tuple ("api_param", "db_column"): Granular with alias mapping

    Examples:
        # Path-based (default)
        invalidation_key_fields = []

        # Granular without aliases (same name in API and DB)
        invalidation_key_fields = ["customer_id", "country_code"]

        # Granular with aliases (API param → DB column)
        invalidation_key_fields = [
            ("customer_id", "user_id"),  # API uses customer_id, DB has user_id
            "country_code",              # Same name in API and DB
        ]
    """

    _listeners_registered = set()
    _redis_client = None  # Singleton Redis connection
    ttl = timedelta(minutes=5)
    model_invalidation_map = {}
    invalidation_key_fields = []  # Empty = path-based, String = same name, Tuple = alias mapping

    def __init__(self, path: str = None):
        self.path = path

        # Use shared Redis connection (singleton)
        if BaseCacheRule._redis_client is None:
            BaseCacheRule._redis_client = self._create_redis_client()

        self.cache = BaseCacheRule._redis_client

        # Only register invalidation events if cache is available
        if self.cache is not None:
            self._register_all_invalidation_events()

    # ---------------- Redis Singleton Setup ----------------

    def _create_redis_client(self):
        """Create a shared Redis/Valkey client safely, reading config from Flask."""
        app = current_app

        # Check if Redis is enabled via ENABLE_REDIS flag
        enable_redis = app.config.get("ENABLE_REDIS", False)

        if not enable_redis:
            print("[Valkey] Redis is disabled via ENABLE_REDIS flag")
            return None

        host = app.config.get("VALKEY_HOST", "valkey-redis")
        port = app.config.get("VALKEY_PORT", 6379)
        ssl = app.config.get("VALKEY_SSL", False)

        try:
            client = Redis(
                host=host,
                port=port,
                ssl=ssl,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            client.ping()
            print(f"[Valkey] Connected to {host}:{port}")
            return client
        except redis_exceptions.ConnectionError as e:
            # Gracefully handle connection failures in ALL environments
            print(f"[Valkey WARNING] Connection failed: {e}")
            return None

    # ---------------- Core cache ops ----------------

    def make_key(self, params: dict) -> str:
        """
        Create cache key with optional metadata tags for granular invalidation.

        Format without tags: /path:hash
        Format with tags: /path:field1=value1:field2=value2:hash

        Args:
            params: Dictionary of parameters to hash

        Returns:
            Cache key string with optional metadata tags

        Note:
            Supports string and tuple formats for invalidation_key_fields:
            - String: "customer_id" (same name in API and DB)
            - Tuple: ("customer_id", "user_id") (API param, DB column)
        """
        raw = json.dumps(params or {}, sort_keys=True)
        digest = hashlib.md5(raw.encode()).hexdigest()

        # Add metadata tags if invalidation_key_fields are defined
        if self.invalidation_key_fields:
            tags = []

            for field in self.invalidation_key_fields:
                # Extract API param name (used in cache key)
                if isinstance(field, tuple):
                    api_param, db_column = field  # Tuple: (api_param, db_column)
                else:
                    api_param = field  # String: same name

                if api_param in params:
                    value = self._format_value(params[api_param])
                    tags.append(f"{api_param}={value}")

            if tags:
                tag_str = ":".join(tags)
                return f"{self.path}:{tag_str}:{digest}"

        return f"{self.path}:{digest}"

    def get(self, key: str):
        if not self.cache:
            return None
        try:
            data = self.cache.get(key)
            return json.loads(data) if data else None
        except redis_exceptions.RedisError as e:
            self._warn(f"get() failed: {e}")
            return None

    def set(self, key: str, data: dict):
        if not self.cache:
            return
        try:
            self.cache.setex(key, int(self.ttl.total_seconds()), json.dumps(data))
        except redis_exceptions.RedisError as e:
            self._warn(f"set() failed: {e}")

    def invalidate_by_path(self):
        """Invalidate all cache entries for this path (path-based invalidation)."""
        if not self.cache or not self.path:
            return
        try:
            deleted = 0
            for key in self.cache.scan_iter(f"{self.path}:*"):
                self.cache.delete(key)
                deleted += 1
            print(f"[Cache] Invalidated {deleted} keys for {self.path}")
        except redis_exceptions.RedisError as e:
            self._warn(f"invalidate_by_path() failed: {e}")

    def invalidate_by_params(self, params: dict):
        """
        Invalidate cache entries matching specific parameters (granular invalidation).

        Uses pattern matching with metadata tags to find and delete matching keys.

        Args:
            params: Dictionary of parameters to match (e.g., {"customer_id": 123})

        Example:
            params = {"customer_id": 123}
            Pattern: /api/profile:customer_id=123:*
            Matches: /api/profile:customer_id=123:abc123...
                     /api/profile:customer_id=123:def456...

        Note:
            Supports string and tuple formats for invalidation_key_fields:
            - String: "customer_id" (same name)
            - Tuple: ("customer_id", "user_id") (API param, DB column)
        """
        if not self.cache or not self.path:
            return

        if not params:
            print("[Cache WARNING] invalidate_by_params called with empty params, falling back to path invalidation")
            self.invalidate_by_path()
            return

        try:
            # Build pattern with metadata tags
            tags = []

            for field in self.invalidation_key_fields:
                # Extract API param name (used in cache key)
                if isinstance(field, tuple):
                    api_param, db_column = field  # Tuple: (api_param, db_column)
                else:
                    api_param = field  # String: same name

                if api_param in params:
                    value = self._format_value(params[api_param])
                    tags.append(f"{api_param}={value}")

            if not tags:
                print("[Cache WARNING] No valid invalidation fields found in params, falling back to path invalidation")
                self.invalidate_by_path()
                return

            # Create pattern: /path:field1=value1:field2=value2:*
            tag_str = ":".join(tags)
            pattern = f"{self.path}:{tag_str}:*"

            deleted = 0
            for key in self.cache.scan_iter(pattern):
                self.cache.delete(key)
                deleted += 1

            print(f"[Cache] Invalidated {deleted} key(s) matching pattern: {pattern}")
        except redis_exceptions.RedisError as e:
            self._warn(f"invalidate_by_params() failed: {e}")

    # ---------------- SQLAlchemy event setup ----------------

    def _register_all_invalidation_events(self):
        for model, cfg in self.model_invalidation_map.items():
            events = cfg.get("events", [])
            columns = cfg.get("columns", [])

            if (model, tuple(events)) in self._listeners_registered:
                continue

            for ev in events:
                event.listen(model, ev, self._invalidation_handler)

            self._listeners_registered.add((model, tuple(events)))
            print(f"[Cache] Registered {model.__name__} → {events}, columns={columns}")

    def _invalidation_handler(self, mapper, connection, target):
        model = target.__class__
        cfg = self.model_invalidation_map.get(model, {})
        watched_cols = cfg.get("columns", [])
        events = cfg.get("events", [])

        state = inspect(target)
        changed = [
            attr.key
            for attr in state.attrs
            if attr.key in watched_cols and attr.history.has_changes()
        ]

        # Invalidate if any configured event fired OR watched columns changed
        if changed or events:
            print(
                f"[Cache] Invalidation triggered by {model.__name__}, changed={changed}"
            )

            # Conditional invalidation based on invalidation_key_fields
            if self.invalidation_key_fields:
                # Granular invalidation - extract params and invalidate specific keys
                invalidation_params = self._extract_invalidation_params(target)
                self.invalidate_by_params(invalidation_params)
            else:
                # Path-based invalidation - invalidate all keys for this path
                self.invalidate_by_path()

    def _extract_invalidation_params(self, target):
        """
        Extract invalidation key field values from the changed model instance.
        Supports field aliases for API param → DB column mapping.

        Args:
            target: SQLAlchemy model instance that triggered the event

        Returns:
            dict: Parameters to use for cache key invalidation (using API param names)

        Examples:
            String format (no aliases):
                invalidation_key_fields = ["customer_id", "country_code"]
                target.customer_id = 123, target.country_code = "sa"
                Returns: {"customer_id": 123, "country_code": "sa"}

            Tuple format (with aliases):
                invalidation_key_fields = [("customer_id", "user_id"), "country_code"]
                target.user_id = 123, target.country_code = "sa"
                Returns: {"customer_id": 123, "country_code": "sa"}
        """
        params = {}

        for field in self.invalidation_key_fields:
            # Extract API param and DB column names
            if isinstance(field, tuple):
                api_param, db_column = field  # Tuple: (api_param, db_column)
            else:
                api_param = db_column = field  # String: same name

            if hasattr(target, db_column):
                value = getattr(target, db_column)
                # Store using API param name (for cache key matching)
                params[api_param] = value
            else:
                print(
                    f"[Cache WARNING] Field '{db_column}' not found on {target.__class__.__name__}"
                )

        return params

    # ---------------- Helpers ----------------

    def _format_value(self, value):
        """
        Format a value for use in cache keys.

        Args:
            value: The value to format (int, str, bool, dict, list, etc.)

        Returns:
            str: Formatted value suitable for cache key
        """
        if isinstance(value, (int, str)):
            return str(value)
        else:
            return json.dumps(value)

    def _warn(self, msg: str):
        print(f"[Valkey WARNING] {msg}")
