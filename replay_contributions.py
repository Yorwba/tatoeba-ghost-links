#!/usr/bin/env python3

import os
import sqlite3
import sys
import time
assert(len(sys.argv) == 2)


DATABASE = 'data/output/replay.sqlite'
try:
    os.remove(DATABASE)
except:
    pass
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
cur.execute(
    '''
    CREATE TABLE sentences (
        id INTEGER PRIMARY KEY,
        present INTEGER)
    ''')
cur.execute(
    '''
    CREATE TABLE links (
        first INTEGER,
        second INTEGER,
        present INTEGER,
        PRIMARY KEY (first, second))
    ''')

logs_trump_database_past_this_point = time.struct_time((2017, 2, 18) + 6*(0,))

with open(sys.argv[1], 'rb') as f:
    full_line = b''
    for line in f:
        full_line += line
        if full_line.endswith(b'\\\n'):
            continue
        username, datetime, action, ctype, sentence_id, \
            sentence_lang, translation_id, text = full_line.split(sep=b'\t', maxsplit=7)
        if datetime == b'0000-00-00 00:00:00':
            datetime = time.struct_time(9*(0,))
        else:
            datetime = time.strptime(datetime.decode('utf-8'), '%Y-%m-%d %H:%M:%S')
        if datetime < logs_trump_database_past_this_point:
            full_line = b''
            continue
        sentence_id = int(sentence_id)
        if ctype == b'sentence':
            if action in (b'insert', b'update'):
                present = 1
            elif action == b'delete':
                present = 0
            else:
                print('Unknown action on sentence: ')
                print(full_line)
                sys.exit(1)
            cur.execute('INSERT OR REPLACE INTO sentences VALUES (?,?)',
                        (sentence_id, present))
        elif ctype == b'link':
            try:
                translation_id = int(translation_id)
            except:
                full_line = b''
                continue
            ends = (sentence_id, translation_id)
            rends = tuple(reversed(ends))
            if action == b'insert':
                present = 1
            elif action == b'delete':
                present = 0
            else:
                print('Unknown action on link: ')
                print(full_line)
                sys.exit(1)
            cur.executemany('INSERT OR REPLACE INTO links VALUES (?,?,?)',
                            (ends+(present,), rends+(present,)))
        elif ctype == b'license':
            pass
        else:
            print('Unknown type of contribution: ')
            print(full_line)
            sys.exit(1)
        full_line = b''

conn.commit()

with open('data/output/replayed_sentences_present.csv', 'w') as f:
    for (sentence_id,) in cur.execute('SELECT id FROM sentences WHERE present = 1 ORDER BY id ASC'):
        f.write(str(sentence_id)+'\n')

with open('data/output/replayed_sentences_deleted.csv', 'w') as f:
    for (sentence_id,) in cur.execute('SELECT id FROM sentences WHERE present = 0 ORDER BY id ASC'):
        f.write(str(sentence_id)+'\n')

with open('data/output/replayed_links_present.csv', 'w') as f:
    for (first, second) in cur.execute('SELECT first, second FROM links WHERE present = 1 ORDER BY first, second ASC'):
        f.write(f'{first}\t{second}\n')

with open('data/output/replayed_links_deleted.csv', 'w') as f:
    for (first, second) in cur.execute('SELECT first, second FROM links WHERE present = 0 ORDER BY first, second ASC'):
        f.write(f'{first}\t{second}\n')
