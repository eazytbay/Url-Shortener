import sqlite3

def initialize_database(db_name: str, schema_file: str):
  """Initializes and sets up the database structure.

  Args:
      db_name (str): The name of the database file.
      schema_file (str): The path to the schema definition file.
  """
  connection = sqlite3.connect(db_name)

  with open(schema_file, 'r') as f:
    connection.executescript(f.read())

  connection.commit()
  connection.close()
