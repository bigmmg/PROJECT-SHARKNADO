import sqlite3

connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

connection.execute('''CREATE TABLE IF NOT EXISTS products
                   ( prodname TEXT NOT NULL,
                   prodcat TEXT NOT NULL,
                   prodid PRIMARY KEY NOT NULL,
                   prodstock INTEGER NOT NULL,
                   prodopid TEXT);''')

connection.commit()

connection.close()