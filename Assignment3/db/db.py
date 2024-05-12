import sqlite3
import sys
import os
from bs4 import BeautifulSoup


current_dir = os.path.dirname(os.path.abspath(__file__))


parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from logic.logic import preprocess_text

def create_connection(db_file):
    """ Create and return a database connection and cursor to the SQLite database specified by db_file """
    conn = sqlite3.connect(db_file)
    return conn, conn.cursor()

def create_tables(c):
    """ Create the necessary database tables """
    c.execute('''
    CREATE TABLE IF NOT EXISTS IndexWord (
        word TEXT PRIMARY KEY
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Posting (
        word TEXT NOT NULL,
        documentName TEXT NOT NULL,
        frequency INTEGER NOT NULL,
        indexes TEXT NOT NULL,
        PRIMARY KEY (word, documentName),
        FOREIGN KEY (word) REFERENCES IndexWord(word)
    );
    ''')

def insert_index_word(c, word):
    """ Insert a word into the IndexWord table """
    c.execute('INSERT OR IGNORE INTO IndexWord (word) VALUES (?)', (word,))

def insert_posting(c, word, document_name, frequency, indexes):
    """ Insert a posting into the Posting table with conflict resolution """
    index_string = ','.join(map(str, indexes))
    c.execute('''
        INSERT INTO Posting (word, documentName, frequency, indexes) 
        VALUES (?, ?, ?, ?) ON CONFLICT(word, documentName) DO UPDATE SET
        frequency=excluded.frequency, indexes=excluded.indexes;
    ''', (word, document_name, frequency, index_string))


def index_document(c, document_name, tokens):
    """ Process tokens and index them into the database """
    from collections import defaultdict
    index_map = defaultdict(list)
    for idx, token in enumerate(tokens):
        index_map[token].append(idx)
    
    for word, indexes in index_map.items():
        insert_index_word(c, word)  # This already uses INSERT OR IGNORE
        # Check if posting already exists
        c.execute('SELECT 1 FROM Posting WHERE word=? AND documentName=?', (word, document_name))
        if c.fetchone():
            # If exists, you can decide to skip or update
            continue  # Just skip in this example
        insert_posting(c, word, document_name, len(indexes), indexes)


def select_all_postings(c):
    """ Print all entries in the Posting table """
    print("Selecting all the data from the Posting table:")
    for row in c.execute("SELECT * FROM Posting"):
        print(f"\t{row}")

def search_documents_containing_words(c, words):
    """ Search for documents that contain specified words and print results """
    print("Get all documents that contain specified words.")
    query = '''
        SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
        FROM Posting p
        WHERE
            p.word IN ({})
        GROUP BY p.documentName
        ORDER BY freq DESC;
    '''.format(','.join('?' for _ in words))  # Safe parameter substitution
    cursor = c.execute(query, words)

    for row in cursor:
        print(f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}")

def search(c, query):
    """ Search the database based on a query and return results """
    query_tokens = preprocess_text(query)
    results = {}
    for token in query_tokens:
        c.execute('SELECT documentName, frequency, indexes FROM Posting WHERE word=?', (token,))
        results[token] = c.fetchall()
    return results

"""# Example usage
conn, c = create_connection('inverted_index.db')
create_tables(c)

# Indexing a document
html_content = '<html><body>This is a sample document with text to index. This document contains important text.</body></html>'
tokens = preprocess_text(html_content)
index_document(c, 'sample_document.html', tokens)
conn.commit()

# Display all postings
#select_all_postings(c)

# Search and display documents containing specific words
#search_documents_containing_words(c, ['Tuš', 'Mercator'])

conn.close()"""

def main():
    conn, c = create_connection('inverted_index.db')
    create_tables(c)
    directories = [
        'data/e-prostor.gov.si/',
        'data/e-uprava.gov.si/',
        'data/evem.gov.si/',
        'data/podatki.gov.si/'
        ]
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as html_file:
                        html_content = html_file.read()
                        tokens = preprocess_text(html_content)
                        index_document(c, file_path, tokens)
    #search_documents_containing_words(c, ['uporablja', 'piškotke'])
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()