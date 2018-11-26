#!/usr/bin/env python3

import os
import sqlite3


DATABASE = 'data/output/rehydrated.sqlite'
try:
    os.remove(DATABASE)
except:
    pass
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
cur.execute(
    '''
    CREATE TABLE sentences (id INTEGER PRIMARY KEY)
    ''')
cur.execute(
    '''
    CREATE TABLE links (first INTEGER, second INTEGER, PRIMARY KEY (first, second))
    ''')

with open('data/tatoeba/sentences.csv', 'rb') as f:
    full_line = b''
    for line in f:
        full_line += line
        if full_line.endswith(b'\\\n'):
            continue
        sentence_id, sentence_lang, text = full_line.split(sep=b'\t', maxsplit=2)
        sentence_id = int(sentence_id)
        cur.execute('INSERT INTO sentences VALUES (?)', (sentence_id,))
        full_line = b''

with open('data/tatoeba/links.csv', 'rb') as f:
    full_line = b''
    for line in f:
        full_line += line
        if full_line.endswith(b'\\\n'):
            continue
        sentence_id, translation_id = full_line.split(sep=b'\t', maxsplit=2)
        sentence_id = int(sentence_id)
        translation_id = int(translation_id)
        cur.execute('INSERT INTO links VALUES (?,?)', (sentence_id, translation_id))
        full_line = b''

conn.commit()
