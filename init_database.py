import sqlite3

conn = sqlite3.connect('complaint.db')

db = conn.cursor()

conn.execute('''CREATE TABLE item (id int, name text, price int, primary key(id))''')
##в одной покупке может быть несколько предметов, поэтому ключ - пара значений:
conn.execute('''CREATE TABLE purchase (id int, item_id int,
customer_id int, time time, date date, primary key(id))''')
conn.execute('''CREATE TABLE customer (id int, name text, surname text,
 patername text, phone number text, email text, primary key(id))''')
conn.execute('''CREATE TABLE complaint (id int, text text, item_id int, purchase_id int, 
primary key(id))''')