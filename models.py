import sqlite3

class Url:
  """
  Represents a shortened URL entry in the database.
  """

  def __init__(self, original_url, clicks=0):
    """
    Initializes a Url object.

    Args:
        original_url (str): The original, full-length URL.
        clicks (int, optional): The number of times the URL has been clicked. Defaults to 0.
    """
    self.original_url = original_url
    self.clicks = clicks

  @classmethod
  def create(cls, original_url):
    """
    Creates a new Url entry in the database.

    Args:
        original_url (str): The original, full-length URL.

    Returns:
        Url: The newly created Url object.
    """
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    sql = """
      INSERT INTO urls (original_url, clicks) VALUES (?, ?)
    """
    cursor.execute(sql, (original_url, 0))
    connection.commit()
    connection.close()

    # Retrieve the newly created entry's ID
    cursor = connection.cursor()
    cursor.execute("SELECT last_insert_rowid()")
    id = cursor.fetchone()[0]
    connection.close()

    return cls(original_url, clicks=0)  # Create a Url object with retrieved ID
