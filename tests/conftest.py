import hashlib
import hmac
import os

import psycopg2
import pytest
from typing import List

from fuzzy_vendor_matching_webhook_python import create_app, config
from fuzzy_vendor_matching_webhook_python.import_vendor_data import db_import, db_drop_vendor_data
from tests import GENERATED_SECRET_KEY, COMPANIES_FILE
from tests.database_janitor import DatabaseJanitor

WEBHOOK_URL = "httpmock://api.elis.rossum.ai/v1/hooks/100"


def create_annotation_tree(
    sender_name="", vendor_vat_id="", sender_address="", vendor_match="---",
) -> List[dict]:
    return [
        {
            "id": "190000",
            "schema_id": "vendor_section",
            "children": [
                {"id": "190001", "schema_id": "sender_name", "content": {"value": sender_name}},
                {
                    "id": "190002",
                    "schema_id": "sender_address",
                    "content": {"value": sender_address},
                },
                {"id": "190003", "schema_id": "vendor_vat_id", "content": {"value": vendor_vat_id}},
                {"id": "190004", "schema_id": "vendor_match", "content": {"value": vendor_match}},
            ],
        }
    ]


def create_hashed_signature(request_body: bytes) -> str:
    signature = hmac.new(GENERATED_SECRET_KEY.encode(), request_body, hashlib.sha1).hexdigest()
    return signature


@pytest.fixture(scope="session")
def monkeysession():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def database(monkeysession):
    """A new fresh DB is created prefixed with test_"""
    database_config = config.DATABASE_CONFIG

    pg_args = (
        database_config["username"],
        database_config["hostname"],
        database_config["port"],
        database_config["password"],
    )
    pg_db = database_config["database"] = f"test_{database_config['database']}"

    with DatabaseJanitor(*pg_args, pg_db, version="11.4", force_init=True):
        connection = psycopg2.connect(
            dbname=pg_db,
            user=database_config["username"],
            password=database_config["password"],
            host=database_config["hostname"],
            port=database_config["port"],
        )

        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        connection.commit()
        monkeysession.setitem(os.environ, "DB_NAME", str(pg_db))
        yield str(pg_db)


@pytest.fixture(scope="session")
def app(database):
    app = create_app()
    yield app


@pytest.fixture
def fill_vendor_data_table():
    db_import(COMPANIES_FILE)
    yield
    db_drop_vendor_data()
