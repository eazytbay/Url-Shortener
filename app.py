import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for


def establish_database_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_short_url(original_url):
    """Creates a shortened URL for the provided original URL.

    Args:
        original_url (str): The original URL to be shortened.

    Returns:
        str: The shortened URL.
    """
    conn = establish_database_connection()

    if not original_url:
        flash('Please enter a URL!')
        return redirect(url_for('retrieve_shorten_form'))  # Route for form

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (original_url) VALUES (?)', (original_url,))
        conn.commit()
        url_id = cursor.lastrowid
        short_url = request.host_url + hashids.encode(url_id)
    except sqlite3.IntegrityError:
        # Handle potential duplicate URL scenario (optional)
        flash('URL already exists! Try a different one.')
        return redirect(url_for('retrieve_shorten_form'))
    finally:
        conn.close()

    return short_url


def retrieve_shorten_form():
    """Retrieves the shorten URL form template."""
    return render_template('index.html')  # Assuming the template name


def redirect_to_original_url(encoded_id):
    """Redirects to the original URL associated with the encoded ID.

    Args:
        encoded_id (str): The encoded ID representing the shortened URL.

    Returns:
        flask.Response: A redirect response to the original URL.
    """
    conn = establish_database_connection()

    try:
        original_id = hashids.decode(encoded_id)[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls WHERE id = (?)', (original_id,)).fetchone()

        if not url_data:
            flash('Invalid URL')
            return redirect(url_for('retrieve_shorten_form'))

        original_url = url_data['original_url']
        clicks = url_data['clicks'] + 1  # Update click count

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?', (clicks, original_id))
        conn.commit()
    except:
        flash('An error occurred. Please try again later.')
        return redirect(url_for('retrieve_shorten_form'))
    finally:
        conn.close()

    return redirect(original_url)


def retrieve_url_statistics():
    """Retrieves URL statistics from the database.

    Returns:
        list: A list of dictionaries containing URL information.
    """
    conn = establish_database_connection()
    db_urls = conn.execute('SELECT id, created, original_url, clicks FROM urls').fetchall()
    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return urls


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "for the night is dark and full of terrors"
    hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

    app.route('/', methods=('GET', 'POST'))(create_short_url)  # Function for handling form submission
    app.route('/<encoded_id>')(redirect_to_original_url)  # Redirect based on encoded ID
    app.route('/stats')(retrieve_url_statistics)  # Route for displaying statistics

    app.run(debug=True)

