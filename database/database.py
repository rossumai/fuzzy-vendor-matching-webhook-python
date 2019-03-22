#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import psycopg2
import threading
import logging

from contextlib import closing

import config

__threadLocal = threading.local()


class Database:
    """self-reconnecting database object"""

    def __init__(self):
        self.db_conn = psycopg2.connect(dbname=config.DATABASE_CONFIG['db_name'],
                                        host=config.DATABASE_CONFIG['host'],
                                        port=config.DATABASE_CONFIG['port'],
                                        user=config.DATABASE_CONFIG['user_name'])

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
            logging.exception('We have invalid input data (SQLi?): level %s (%s) @%s' % (
                level, error, time.strftime('%Y%m%d %a %I:%m %p')
            ))
            self.db_conn.rollback()
            raise RuntimeError('Non-sanitized data entered again... BOBBY TABLES')
        except psycopg2.IntegrityError:
            # This is not an error that deserves to be treated
            # as dropped connection.

            raise
        except Exception as error:
            logging.exception('Sleeping: level %s (%s) @%s' % (
                level, error, time.strftime('%Y%m%d %a %I:%m %p')
            ))
            time.sleep(min(2 ** level, 30))
            try:
                self.db_conn = psycopg2.connect(dbname=config.DATABASE_CONFIG['db_name'],
                                                host=config.DATABASE_CONFIG['host'],
                                                port=config.DATABASE_CONFIG['port'],
                                                user=config.DATABASE_CONFIG['user_name'])
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


class DEDatabase(Database):
    def __init__(self):
        super().__init__()
