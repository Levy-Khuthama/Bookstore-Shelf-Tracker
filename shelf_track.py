"""Bookstore shelf tracking program.

The program stores book and author details in a local SQLite database
called ebookstore.db.
"""

import sqlite3
from contextlib import contextmanager


DATABASE = "ebookstore.db"
ID_LENGTH = 4
LINE_LENGTH = 50


STARTER_AUTHORS = [
    (1290, "Charles Dickens", "England"),
    (8937, "J.K. Rowling", "England"),
    (2356, "C.S. Lewis", "Ireland"),
    (6380, "J.R.R. Tolkien", "South Africa"),
    (5620, "Lewis Carroll", "England"),
]

STARTER_BOOKS = [
    (3001, "A Tale of Two Cities", 1290, 30),
    (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
    (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
    (3004, "The Lord of the Rings", 6380, 37),
    (3005, "Alice's Adventures in Wonderland", 5620, 12),
]


@contextmanager
def database_connection():
    """Open a database connection and close it automatically."""
    conn = None

    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


def create_tables():
    """Create the author and book tables if they do not already exist."""
    with database_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS author (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                authorID INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                FOREIGN KEY (authorID) REFERENCES author(id)
            )
        """)


def populate_tables():
    """Insert the starter authors and books."""
    with database_connection() as conn:
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT OR IGNORE INTO author (id, name, country)
            VALUES (?, ?, ?)
        """, STARTER_AUTHORS)

        cursor.executemany("""
            INSERT OR IGNORE INTO book (id, title, authorID, qty)
            VALUES (?, ?, ?, ?)
        """, STARTER_BOOKS)


def get_non_empty_text(prompt):
    """Ask for text until the user enters a non-empty value."""
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("Input cannot be blank.")


def get_optional_text(prompt, current_value):
    """Return new text, or the current value if the user presses Enter."""
    value = input(prompt).strip()

    if value == "":
        return current_value

    return value


def get_valid_integer(prompt):
    """Ask the user for an integer until they enter a valid one."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid whole number.")


def get_valid_id(prompt):
    """Ask for a four-digit integer ID."""
    while True:
        value = input(prompt).strip()

        if value.isdigit() and len(value) == ID_LENGTH:
            return int(value)

        print("Invalid ID. Please enter exactly four digits.")


def get_valid_quantity(prompt):
    """Ask for a quantity that is zero or greater."""
    while True:
        quantity = get_valid_integer(prompt)

        if quantity >= 0:
            return quantity

        print("Quantity cannot be negative.")


def author_exists(cursor, author_id):
    """Return True if an author exists in the database."""
    cursor.execute("SELECT id FROM author WHERE id = ?", (author_id,))
    return cursor.fetchone() is not None


def add_author(cursor, author_id):
    """Add a new author for a book being entered."""
    print("No author found with that ID. Please enter the author's details.")

    name = get_non_empty_text("Enter author's name: ")
    country = get_non_empty_text("Enter author's country: ")

    cursor.execute("""
        INSERT INTO author (id, name, country)
        VALUES (?, ?, ?)
    """, (author_id, name, country))


def enter_book():
    """Add a new book to the database."""
    print("\nEnter book")

    book_id = get_valid_id("Enter book ID: ")
    title = get_non_empty_text("Enter title: ")
    author_id = get_valid_id("Enter author ID: ")
    quantity = get_valid_quantity("Enter quantity: ")

    try:
        with database_connection() as conn:
            cursor = conn.cursor()

            if not author_exists(cursor, author_id):
                add_author(cursor, author_id)

            cursor.execute("""
                INSERT INTO book (id, title, authorID, qty)
                VALUES (?, ?, ?, ?)
            """, (book_id, title, author_id, quantity))

        print("Book added successfully.")
    except sqlite3.IntegrityError:
        print("A book with that ID already exists.")
    except sqlite3.Error as error:
        print(f"Insert error: {error}")


def get_book_author_details(cursor, book_id):
    """Fetch a book title with its author's ID, name, and country."""
    cursor.execute("""
        SELECT book.title, author.id, author.name, author.country
        FROM book
        INNER JOIN author ON book.authorID = author.id
        WHERE book.id = ?
    """, (book_id,))

    return cursor.fetchone()


def update_book():
    """Update the author details linked to a selected book."""
    print("\nUpdate book")
    book_id = get_valid_id("Enter book ID to update: ")

    with database_connection() as conn:
        cursor = conn.cursor()
        book = get_book_author_details(cursor, book_id)

        if book is None:
            print("No book found with that ID.")
            return

        title, author_id, author_name, author_country = book

        print(
            f"\nCurrent book: {title}\n"
            f"Author's Name: {author_name}\n"
            f"Author's Country: {author_country}"
        )

        new_name = get_optional_text(
            "Enter new author's name, or press Enter to keep current: ",
            author_name
        )
        new_country = get_optional_text(
            "Enter new author's country, or press Enter to keep current: ",
            author_country
        )

        cursor.execute("""
            UPDATE author
            SET name = ?, country = ?
            WHERE id = ?
        """, (new_name, new_country, author_id))

    print("Author information updated successfully.")


def delete_book():
    """Delete a book from the database."""
    print("\nDelete book")
    book_id = get_valid_id("Enter ID of the book you want to delete: ")

    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))

        if cursor.rowcount == 0:
            print("No book found with that ID.")
            return

    print("Book deleted successfully.")


def display_books(books):
    """Display book rows in a readable table."""
    if not books:
        print("No books found.")
        return

    print("\nID    Title                                      AuthorID  Qty")
    print("-" * 65)

    for book in books:
        print(f"{book[0]:<5} {book[1]:<42} {book[2]:<8} {book[3]}")


def search_books():
    """Search for books by ID, title, author ID, or show all books."""
    print("\nSearch books")
    print("1. Search by ID")
    print("2. Search by title")
    print("3. Search by author ID")
    print("4. Show all books")

    choice = input("Choose a search option: ").strip()

    with database_connection() as conn:
        cursor = conn.cursor()

        if choice == "1":
            book_id = get_valid_id("Enter book ID: ")
            cursor.execute("SELECT * FROM book WHERE id = ?", (book_id,))
        elif choice == "2":
            title = get_non_empty_text("Enter title or part of title: ")
            cursor.execute(
                "SELECT * FROM book WHERE title LIKE ?",
                (f"%{title}%",)
            )
        elif choice == "3":
            author_id = get_valid_id("Enter author ID: ")
            cursor.execute(
                "SELECT * FROM book WHERE authorID = ?",
                (author_id,)
            )
        elif choice == "4":
            cursor.execute("SELECT * FROM book ORDER BY id")
        else:
            print("Invalid search option.")
            return

        display_books(cursor.fetchall())


def display_book_details(records):
    """Display book titles with author names and countries."""
    if not records:
        print("No book details found.")
        return

    titles = [record[0] for record in records]
    author_names = [record[1] for record in records]
    author_countries = [record[2] for record in records]

    print("\nDetails")
    for title, author_name, author_country in zip(
        titles,
        author_names,
        author_countries
    ):
        print("-" * LINE_LENGTH)
        print(f"Title: {title}")
        print(f"Author's Name: {author_name}")
        print(f"Author's Country: {author_country}")

    print("-" * LINE_LENGTH)


def view_all_book_details():
    """Display every book with its author's name and country."""
    with database_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT book.title, author.name, author.country
            FROM book
            INNER JOIN author ON book.authorID = author.id
            ORDER BY book.id
        """)

        display_book_details(cursor.fetchall())


def display_menu():
    """Display the main menu."""
    print("\nBookstore Shelf Tracking Program")
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View details of all books")
    print("0. Exit")


def menu():
    """Display the menu and call the selected function."""
    menu_actions = {
        "1": enter_book,
        "2": update_book,
        "3": delete_book,
        "4": search_books,
        "5": view_all_book_details,
    }

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Exiting program. \nGoodbye!")
            break

        action = menu_actions.get(choice)

        if action is None:
            print("Invalid choice. Please choose 0, 1, 2, 3, 4, or 5.")
            continue

        try:
            action()
        except sqlite3.Error as error:
            print(f"Database error: {error}")


def main():
    """Create the database tables, add starter data, and start the menu."""
    try:
        create_tables()
        populate_tables()
    except sqlite3.Error as error:
        print(f"Could not prepare the database: {error}")
        return

    menu()


if __name__ == "__main__":
    main()
