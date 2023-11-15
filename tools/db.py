import sqlite3

# Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect("../data/data.db")

# Create a cursor object using the cursor method
cursor = conn.cursor()

# SQL statement to create a table named 'units'
create_table_units = """
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY,
    name TEXT
);
"""

# SQL statement to create a table named 'dates'
create_table_dates = """
CREATE TABLE IF NOT EXISTS dates (
    date DATE PRIMARY KEY,
    day_id INTEGER,
    day_name TEXT,
    mo_start INTEGER,
    mo_end INTEGER,
    aft_start INTEGER,
    aft_end INTEGER
);
"""

create_table_dates = """
CREATE TABLE IF NOT EXISTS holidays (
    date DATE PRIMARY KEY,
    name TEXT,
    morning INTEGER,
    afternoon INTEGER
);
"""

# Execute the SQL statement to create tables
cursor.execute(create_table_units)
cursor.execute(create_table_dates)

# Commit the transaction
conn.commit()

# Close the database connection
conn.close()
