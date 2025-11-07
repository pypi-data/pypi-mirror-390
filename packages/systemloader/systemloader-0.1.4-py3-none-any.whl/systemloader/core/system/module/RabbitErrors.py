from collections import defaultdict


class RabbitErrors:
    def __init__(self, error_list=None):
        self.errors = None
        self.set_errors()
        if error_list and isinstance(error_list, list):
            for error in error_list:
                self.add_message(error['code'], error['field'], error.get('text'))

    def set_errors(self, value_dict: dict | None = None) -> None:
        self.errors = defaultdict(dict, value_dict) if value_dict else defaultdict(dict)

    def add_message(self, code: str, field: str, message: str | None = None):
        self.errors[code].setdefault(str(field) if field else None, set()).add(message)
        # self.errors[code].add(str(message))

    def get(self) -> list:
        errors = []
        for code, field_messages in self.errors.items():
            for field, messages in field_messages.items():
                error = {
                    'code': code,
                    'field': field,
                }
                if error_text := ', '.join(message for message in messages if message and isinstance(message, str)):
                    error['text'] = error_text
                errors.append(error)
        return errors
        # return [{'code': code, 'field': ', '.join(message)} for code, message in self.errors.items()]

    def is_empty(self) -> bool:
        return not self.errors

    def __add__(self, other):
        if isinstance(other, RabbitErrors):
            obj = RabbitErrors()
            obj.set_errors({**self.errors, **other.errors})
            return obj

    def __iadd__(self, other):
        if isinstance(other, RabbitErrors):
            self.set_errors({**self.errors, **other.errors})
            return self


if __name__ == "__main__":
    rabbit_error = RabbitErrors()
    print(rabbit_error.is_empty())
    rabbit_error.add_message('test1', 'aaa1')
    rabbit_error.add_message('test1', 'aaa', 'msg_02')
    rabbit_error.add_message('test1', 'aaa', 'msg02')
    rabbit_error2 = RabbitErrors()
    rabbit_error.add_message('test1', 'aaa', 'msg_02')
    rabbit_error2 += rabbit_error
    print(rabbit_error.is_empty())
    print(rabbit_error2.get())
