import sqlite3
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from db.db import create_connection, search_documents_containing_words

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn, conn.cursor()


if len(sys.argv) < 2:
    print("Usage: run-basic-search.py SEARCH_PARAM")
    sys.exit(1)

search_param_str = sys.argv[1]
search_params = search_param_str.lower().split()
print(f"Searching for documents containing words: {search_params}")

conn, c = create_connection('db\inverted_index.db')

search_documents_containing_words(c, search_params)

