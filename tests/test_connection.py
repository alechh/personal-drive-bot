import sys
import os
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_folder)

from utils.db_connector import DB_Connector
from decouple import config
import pytest

def test_db_connector():
    db = DB_Connector("localhost", 5432, "alechh", "123", "postgres")
    assert db.connect() != None