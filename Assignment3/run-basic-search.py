import sqlite3
import sys
import os

# Determine the current and parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the necessary functions from db module
from db.db import create_connection, search_documents_containing_words

# Function to create a database connection
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn, conn.cursor()


if len(sys.argv) < 2:
    print("Usage: run-basic-search.py SEARCH_PARAM")
    sys.exit(1)

# Read and process the SEARCH_PARAM from command-line arguments
search_param_str = sys.argv[1]
search_params = search_param_str.lower().split()
print(f"Searching for documents containing words: {search_params}")

# Create database connection
conn, c = create_connection('db\inverted_index.db')

# Execute the search
search_documents_containing_words(c, search_params)

