import ast
import json
from functools import wraps

from sqlalchemy.orm.base import object_mapper
import flask_sqlalchemy
from flask import request
from marshmallow import ValidationError
from sqlalchemy.orm.exc import UnmappedInstanceError

from wedeliver_core_plus.helpers.exceptions import AppValidationError


def is_mapped(obj):
    try:
        data = obj
        if isinstance(data, list) and len(data):
            data = obj[0]
        object_mapper(data)
    except UnmappedInstanceError:
        return False
    return True

def is_result_row(obj):
    try:
        data = obj
        if isinstance(data, list) and len(data):
            data = obj[0]

        if hasattr(data, '__row_data__'):
            return True
    except UnmappedInstanceError:
        return False
    return False


def serializer(path, schema=None, many=False, cache_rule=None):
    def factory(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            # user_language = Auth.get_user_language()
            # with force_locale(user_language):
            is_function_with_validated_data = False
            if hasattr(func, '__wrapped__'):
                old_vars = func.__wrapped__.__code__.co_varnames
                is_function_with_validated_data = old_vars.__contains__('validated_data')

            appended_kws = kwargs.pop('appended_kws', None)

            try:
                client_data = dict()

                if kwargs:
                    client_data.update(**kwargs)

                content_type = request.headers.get('Content-Type')
                if content_type and 'application/json' in content_type:
                    # if the request have json payload, the user need to send the Content-Type as application/json
                    try:
                        client_data.update(request.json)
                    except Exception:
                        pass

                elif request.form:
                    client_data.update(request.form.to_dict())

                    def _sanitize(cd):
                        for _k in cd.keys():
                            try:
                                value = ast.literal_eval(cd[_k])
                                if isinstance(value, int):
                                    value = str(value)
                                cd[_k] = value
                            except Exception:
                                try:
                                    value = json.loads(cd[_k])
                                    if isinstance(value, list):
                                        output = []
                                        for _v in value:
                                            output.append(_sanitize(_v))
                                        cd[_k] = output
                                    if isinstance(value, dict):
                                        cd[_k] = _sanitize(value)
                                except Exception:
                                    pass
                        return cd

                    _sanitize(client_data)

                if request.args:
                    client_data.update(request.args.to_dict())

                inputs = client_data  # .to_dict()
                if appended_kws:
                    inputs.update(appended_kws)

                if schema:
                    result = schema(many=many).load(inputs)
                else:
                    result = inputs
            except ValidationError as e:
                raise AppValidationError(e.messages)

            if result:
                if is_function_with_validated_data:
                    kwargs.update(dict(validated_data=result))
            # if schema and request.method == "GET":

            # ---------------- Cache logic BEFORE function call ----------------
            cache_instance = None
            cache_key = None
            if cache_rule:
                request_data = kwargs.get("validated_data", {})
                # Initialize the rule (it may auto-register SQLAlchemy listeners)
                # Pass path into the cache rule instance
                cache_instance = cache_rule(path)
                # Use path + request args/body as key
                cache_key = cache_instance.make_key(request_data)
                cached_data = cache_instance.get(cache_key)
                if cached_data is not None:
                    print(f"[Cache] HIT for {path}")

                    # Add is_cached flag if response is dict or list
                    if isinstance(cached_data, dict):
                        cached_data["is_cached"] = True
                    elif isinstance(cached_data, list):
                        # Loop through list and add is_cached to each dict element
                        for item in cached_data:
                            if isinstance(item, dict):
                                item["is_cached"] = True

                    return cached_data  # 🟢 return from cache immediately

            # ---------------- Execute main function ----------------

            try:
                result = func(*args, **kwargs)
                if isinstance(result, flask_sqlalchemy.Pagination):
                    items = schema(many=isinstance(result.items, list)).dump(result.items)
                    output = dict(
                        items=items,
                        total=result.total,
                        next_num=result.next_num,
                        prev_num=result.prev_num,
                        page=result.page,
                        per_page=result.per_page
                    )
                elif is_mapped(result) or is_result_row(result):  # is model instance
                    output = schema(many=isinstance(result, list)).dump(result)
                else:
                    output = result
            except ValidationError as e:
                raise AppValidationError(e.messages)

            # ---------------- Cache AFTER execution ----------------
            if cache_instance and cache_key and output is not None:
                cache_instance.set(cache_key, output)

            return output

            # return func(*args, **kwargs)

        return decorator

    return factory
