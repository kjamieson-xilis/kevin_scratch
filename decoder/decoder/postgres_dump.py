import base64
import os

import psycopg2

conn = psycopg2.connect(f"host=xilishub-frontendstack-readonly.cfa8q6p9zylh.us-east-1.rds.amazonaws.com user=postgres password={os.getenv('POSTGRES_PASSWORD')} dbname='XilisHub - FrontendStack'")

cur = conn.cursor()
cur.execute('SELECT * FROM "labCollectorFiles"')

for index, line in enumerate(cur.fetchall()):
    stripped = line[1].strip('\n')
    try:
        data = base64.b64decode(stripped)
        with open(f'./data_out_{index}.xlsx', 'wb') as f:
            f.write(data)
    except Exception as e:
        print(f"Failed on index {index}, {e}")
        print(line)
        pass
