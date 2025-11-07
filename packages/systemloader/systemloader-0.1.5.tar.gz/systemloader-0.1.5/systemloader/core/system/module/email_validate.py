import re

EMAIL_REGEX = re.compile(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$')


def email_validate(email: str) -> bool:
    res = bool(EMAIL_REGEX.match(email))
    return res


if __name__ == '__main__':
    print(email_validate('abc@abc.ru'))
    print(email_validate('abc@abc'))
    print(email_validate('!abc@abc.ru'))
