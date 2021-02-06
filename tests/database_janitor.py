from contextlib import contextmanager
from typing import Union

import psycopg2
from psycopg2._psycopg import cursor
from psycopg2.errorcodes import DUPLICATE_DATABASE
from pytest_postgresql.janitor import DatabaseJanitor as DatabaseJanitorOrig, Version


class DatabaseJanitor(DatabaseJanitorOrig):
    def __init__(
        self,
        user: str,
        host: str,
        port: str,
        password: str,
        db_name: str,
        *,
        version: Union[str, float, Version],
        force_init: bool = False,
    ) -> None:
        super().__init__(user, host, port, db_name, version=version)
        self.password = password
        self.force_init = force_init

    def init(self) -> None:
        try:
            super().init()
        except Exception as e:
            if not (getattr(e, "pgcode", None) == DUPLICATE_DATABASE and self.force_init):
                raise e
            self.drop()
            super().init()

    @contextmanager
    def cursor(self, **kwargs) -> cursor:
        """Return postgresql cursor."""
        conn = psycopg2.connect(
            user=self.user, host=self.host, port=self.port, password=self.password, **kwargs
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
            conn.close()
