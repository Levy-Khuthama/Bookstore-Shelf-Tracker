# Bookstore-Shelf-Tracker
A command-line program for managing a bookstore's stock, built with Python and SQLite. It stores books and their authors in a local database and lets you add, update, delete and search records from a simple menu.

This project was completed as part of the Artificial Intelligence online bootcamp (Stellenbosch University in partnership with HyperionDev).

Features
Enter book: adds a new book. If the author ID isn't in the database yet, the program asks for the author's name and country and adds the author first.
Update book: looks up a book by ID, shows its current author's name and country, and lets you change them (press Enter to keep a value).
Delete book: removes a book by ID.
Search books: by book ID, by title (partial matches work), by author ID, or show all books.
View details of all books: lists every book with its author's name and country, using a join across the two tables.
Bookstore Shelf Tracking Program
1. Enter book
2. Update book
3. Delete book
4. Search books
5. View details of all books
0. Exit
How it works

Database design: two related tables in ebookstore.db.

Table	Columns
author	id (primary key), name, country
book	id (primary key), title, authorID (foreign key to author.id), qty

One author can have many books. On first run the program creates the tables and fills them with five starter books and authors; running it again doesn't create duplicates (INSERT OR IGNORE).

Good practices used

Parameterised queries everywhere, so user input can't alter the SQL (protects against SQL injection).
Foreign keys enforced (PRAGMA foreign_keys = ON), so a book can't point to an author that doesn't exist.
A context manager opens each connection, commits on success, rolls back on database errors and always closes the connection.
Input validation: IDs must be exactly four digits, quantities can't be negative, text can't be blank, and invalid menu choices are handled.
Atomic inserts: if adding a book fails (for example a duplicate book ID), a new author added in the same step is rolled back too.
Small, single-purpose functions with docstrings, and the menu is driven by a dictionary of functions.
How to run

You need Python 3. There are no extra packages to install, because sqlite3 is part of the standard library.

bash
python shelf_track.py

The ebookstore.db file is created in the folder you run the program from.

Starter data
Book ID	Title	Author	Qty
3001	A Tale of Two Cities	Charles Dickens	30
3002	Harry Potter and the Philosopher's Stone	J.K. Rowling	40
3003	The Lion, the Witch and the Wardrobe	C.S. Lewis	25
3004	The Lord of the Rings	J.R.R. Tolkien	37
3005	Alice's Adventures in Wonderland	Lewis Carroll	12
Ideas for improvement
Let "Update book" change the quantity and title, not just author details.
Show author names (not just author IDs) in search results.
Check for a duplicate book ID before asking for new author details.
Offer to remove authors who no longer have any books.
Add unit tests using an in-memory SQLite database.
Tech stack

Python 3 · SQLite (sqlite3)
