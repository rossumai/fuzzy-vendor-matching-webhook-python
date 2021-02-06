#!/usr/bin/env python3
import os
from typing import Dict

SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "secret")


def get_database_config() -> Dict[str, str]:
    return {
        "database": os.getenv("DB_NAME", "data_matching"),
        "hostname": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "username": os.getenv("DB_USERNAME", "postgres"),
        "password": os.getenv("DB_PASSWORD", "secret"),
    }


# Database configuration
DATABASE_CONFIG = get_database_config()
