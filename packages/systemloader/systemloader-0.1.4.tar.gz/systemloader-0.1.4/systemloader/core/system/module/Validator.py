import orjson
from pydantic import ValidationError
from functools import wraps

class Validator:
    @staticmethod
    def error_pydantic_convert(errors):
        errors_result = []
        for error in errors:
            error_field = '.'.join(list(map(str, error.get('loc') or '')))
            if not error_field and error['msg'].lower().startswith(error['type'].replace('_', ' ')):
                len_error_type = len(error['type'])
                error_field = error['msg'][:len_error_type]
                error['msg'] = error['msg'][len_error_type + 2:]
            msg_list = error['msg'].split('|', maxsplit=1)
            is_my_error_field = len(msg_list) == 2
            el = {
                'code': error['type'] and error['type'].upper(),
                'field': (msg_list[0] if is_my_error_field and msg_list[0] else error_field).upper(),
                'text': msg_list[1] if is_my_error_field else error['msg'],
            }
            errors_result.append(el)
        return errors_result

    def validate_json(self, class_validate, data, return_json=False, unpack=True):
        try:
            msg_dict = orjson.loads(data) if unpack else data
            msg_obj = class_validate(**msg_dict)
            return msg_dict if return_json else msg_obj, None
        except (orjson.JSONDecodeError, TypeError) as err:
            return None, [{'code': 0, 'field': f"{err.__class__.__name__}", 'text': f"{err}"}]
        except ValidationError as err:
            return None, self.error_pydantic_convert(orjson.loads(err.json()))

    def validate(self, **kwargs_decorator):
        def wrapper(fnc):
            @wraps(fnc)
            async def func_decorated(self_worker, route, message, message_num, **kwargs_worker):
                try:
                    msg_json = message.body
                except AttributeError:
                    msg_json = message
                if class_validate_header := kwargs_decorator.get('validate_header'):
                    msg_validate, error_list = self.validate_json(class_validate_header, msg_json)
                    if not error_list:
                        kwargs_worker['msg_json'] = msg_json
                        return await fnc(self_worker, route, msg_validate, message_num, **kwargs_worker)
                    else:
                        self_worker.logger.error(f"Сообщение #{message_num} -> {error_list}")
                return True

            return func_decorated

        return wrapper
