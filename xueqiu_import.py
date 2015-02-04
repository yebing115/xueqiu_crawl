import json
import sqlite3
import pymongo

conn = sqlite3.connect('data/result.db')
c = conn.cursor()

client = pymongo.MongoClient()
db = client.xueqiudb;
users = db.users;

def save_users(users_arr):
    for user in users_arr:
        if not users.find_one({'id':user['id']}):
            print 'add one user: %d\n' % user['id']
            users.insert(user)

for row in c.execute('select * from resultdb_xueqiu'):
    url = row[1]
    if url.find('members') > 0:
        save_users(json.loads(row[2])['users'])
    elif url.find('followers') > 0:
        save_users(json.loads(row[2])['followers'])
    else:
        continue

client.close()
conn.close()
