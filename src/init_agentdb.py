import sqlite3

con = sqlite3.connect('agent.db')
cur = con.cursor()
cur.execute("CREATE TABLE characters(id integer PRIMARY KEY, name text, description text, pictureurl text)")
con.commit()