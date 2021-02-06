#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import threading
import time
from contextlib import closing
import psycopg2
from fuzzy_vendor_matching_webhook_python.config import get_database_config

__threadLocal = threading.local()


class Database:
    username = None
    password = None
    database = None
    hostname = None
    _db_conn = None

    """self-reconnecting database object"""

    @property
    def db_conn(self):
        if self._db_conn:
            return self._db_conn

        database_config = get_database_config()
        self.username = database_config["username"]
        self.password = database_config["password"]
        self.database = database_config["database"]
        self.hostname = database_config["hostname"]

        self._db_conn = psycopg2.connect(
            dbname=self.database, host=self.hostname, user=self.username, password=self.password,
        )
        return self._db_conn

    def execute(self, query, attrs=None):
        """execute a query and return one result"""
        with closing(self.db_conn.cursor()) as cur:
            cur = self._execute(cur, query, attrs)

    def execute_and_fetch(self, query, attrs=None):
        """execute a query and return one result"""
        with closing(self.db_conn.cursor()) as cur:
            cur = self._execute(cur, query, attrs)
            return cur.fetchone()

    def execute_and_fetchall(self, query, attrs=None):
        """execute a query and return all results"""
        with closing(self.db_conn.cursor()) as cur:
            cur = self._execute(cur, query, attrs)
            return cur.fetchall()

    def _execute(self, cur, query, attrs, level=1):
        """execute a query, and in case of OperationalError (db restart)
        reconnect to database. Recursion with increasing pause between tries"""
        try:
            if attrs is None:
                cur.execute(query)
            else:
                cur.execute(query, attrs)
            return cur
        except psycopg2.DataError as error:  # when biitr comes and enters '99999999999999999999' for amount
            logging.exception(
                "We have invalid input data (SQLi?): level %s (%s) @%s"
                % (level, error, time.strftime("%Y%m%d %a %I:%m %p"))
            )
            self.db_conn.rollback()
            raise RuntimeError("Non-sanitized data entered again... BOBBY TABLES")
        except psycopg2.IntegrityError:
            # This is not an error that deserves to be treated
            # as dropped connection.

            raise
        except Exception as error:
            logging.exception(
                "Sleeping: level %s (%s) @%s" % (level, error, time.strftime("%Y%m%d %a %I:%m %p"))
            )
            time.sleep(min(2 ** level, 30))
            try:
                self.db_conn = psycopg2.connect(
                    dbname=self.database,
                    host=self.hostname,
                    user=self.username,
                    password=self.password,
                )
            except:
                time.sleep(1)
            cur = self.db_conn.cursor()
            return self._execute(cur, query, attrs, level + 1)

    def commit(self):
        """pass commit to db"""
        self.db_conn.commit()

    def rollback(self):
        """roll back the latest transaction"""
        self.db_conn.rollback()


class VendorDatabase(Database):
    def __init__(self):
        super().__init__()
