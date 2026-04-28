import uuid
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def __init__(self):
        super().__init__(36)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value