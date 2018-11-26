#!/usr/bin/env python3

import os
import sqlite3


DATABASE = 'data/output/replay.sqlite'
os.remove(DATABASE)
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

with open('data/tatoeba/contributions.csv', 'rb') as f:
    full_line = b''
    for line in f:
        full_line += line
        if full_line.endswith(b'\\\n'):
            continue
        username, datetime, action, ctype, sentence_id, \
            sentence_lang, translation_id, text = full_line.split(sep=b'\t', maxsplit=7)
        sentence_id = int(sentence_id)
        if ctype == b'sentence':
            if action == b'insert':
                cur.execute('INSERT OR IGNORE INTO sentences VALUES (?)', (sentence_id,))
            elif action == b'delete':
                cur.execute('DELETE FROM sentences WHERE id = ?', (sentence_id,))
            elif action == b'update':
                pass
            else:
                print('Unknown action on sentence: ')
                print(full_line)
        elif ctype == b'link':
            try:
                translation_id = int(translation_id)
            except:
                full_line = b''
                continue
            ends = (sentence_id, translation_id)
            rends = tuple(reversed(ends))
            if action == b'insert':
                cur.executemany('INSERT OR IGNORE INTO links VALUES (?,?)',
                                (ends, rends))
            elif action == b'delete':
                cur.execute('DELETE FROM links WHERE first = ? AND second = ? OR first = ? AND second = ?',
                            ends + rends)
            else:
                print('Unknown action on link: ')
                print(full_line)
        elif ctype == b'license':
            pass
        else:
            print('Unknown type of contribution: ')
            print(full_line)
        full_line = b''

conn.commit()

with open('data/output/replayed_sentences.csv', 'w') as f:
    for (sentence_id,) in cur.execute('SELECT id FROM sentences ORDER BY id ASC'):
        f.write(str(sentence_id)+'\n')

with open('data/output/replayed_links.csv', 'w') as f:
    for (first, second) in cur.execute('SELECT first, second FROM links ORDER BY first, second ASC'):
        f.write(f'{first}\t{second}\n')
