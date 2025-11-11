import json
from datetime import date, datetime
from typing import Any, Self

from sqlalchemy.engine import Dialect
from sqlalchemy.types import Integer, String, Text, TypeDecorator


class DBListJson(TypeDecorator):
    impl = Text

    def load_dialect_impl(self: Self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(Text)

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> str | None:
        """Handle value before getting into the DB"""
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("this type should only be used for lists")
        return json.dumps(value)

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> list | None:
        """Handle values from the database"""
        if value is None:
            return None

        res = json.loads(value)
        if not isinstance(res, list):
            raise ValueError("this type should only be used for lists")

        return res


class DBObjectJson(TypeDecorator):
    impl = Text

    def load_dialect_impl(self: Self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(Text)

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> str | None:
        """Handle value before getting into the DB"""
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"this type should only be used for dicts, got {type(value)}")
        return json.dumps(value)

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> dict | None:
        """Handle values from the database"""
        if value is None:
            return None

        res = json.loads(value)
        if res == []:
            res = {}
        if not isinstance(res, dict):
            raise ValueError(f"this type should only be used for dicts got: {type(res)}")

        return res


class DBUUID(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self: Self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(String(36))

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return str(value)

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> str:
        return value


class DateTimeEpoch(TypeDecorator):
    impl = Integer

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> int | None:
        if isinstance(value, datetime):
            return int(value.timestamp())
        elif isinstance(value, date):
            return int(datetime.combine(value, datetime.min.time()).timestamp())
        return value

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> datetime | None:
        if value is not None:
            return datetime.fromtimestamp(value)
        return value
