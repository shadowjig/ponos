from Ponos import init_db
from env_vars import *
import sqlite3
import os

print(DB_PATH)
open(DB_PATH, 'w').close()
init_db()
