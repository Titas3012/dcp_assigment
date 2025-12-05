# Starter code for Data Centric Programming Assignment 2025

# os is a module that lets us access the file system

# Bryan Duggan likes Star Trek
# Bryan Duggan is a great flute player

import os
import sqlite3
from typing import List, Dict, Optional
import pandas as pd


print(">>> main.py started")

# CONFIG

BOOKS_DIR = "abc_books"
DB_PATH = "tunes.db"

# EXAMPLE DB FUNCTIONS FROM STARTER 

def do_databasse_stuff() -> None:
    """
    Example function from the starter code showing basic sqlite usage.
    Not used by the main application.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, age INTEGER)")

    # Insert data
    cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("John", 30))

    # Save changes
    conn.commit()

    cursor.execute("SELECT * FROM users")

    # Get all results
    results = cursor.fetchall()

    # Print results
    for row in results:
        print(row)
        print(row[0])
        print(row[1])

    df = pd.read_sql("SELECT * FROM users", conn)
    print(df.head())
    conn.close()


def my_sql_database() -> None:
    """
    Example MySQL usage from starter code (not used in main flow).
    Requires a running MySQL instance and tunepal DB.
    """
    conn = mysql.connector.connect(host="localhost", user="root", database="tunepal")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tuneindex")

    while True:
        row = cursor.fetchone()
        if not row:
            break
        else:
            print(row)

    conn.close()

# DATABASE SETUP & INSERT

def init_db(db_path: str = DB_PATH, reset: bool = False) -> sqlite3.Connection:
    """
    Initialise the SQLite database and create the tunes table if needed.

    Args:
        db_path: Path to the sqlite database file.
        reset: If True, drop and recreate the tunes table.

    Returns:
        sqlite3.Connection object.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS tunes")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book INTEGER,
            filename TEXT,
            tune_ref TEXT,
            title TEXT,
            rhythm TEXT,
            meter TEXT,
            key TEXT,
            abc TEXT
        )
        """
    )
    conn.commit()
    return conn


def insert_tunes(conn: sqlite3.Connection, tunes: List[Dict]) -> None:
    """
    Insert a list of tune dictionaries into the tunes table.

    Args:
        conn: Open sqlite connection.
        tunes: List of dictionaries, each representing one tune.
    """
    if not tunes:
        return

    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO tunes (book, filename, tune_ref, title, rhythm, meter, key, abc)
        VALUES (:book, :filename, :tune_ref, :title, :rhythm, :meter, :key, :abc)
        """,
        tunes,
    )
    conn.commit()

# ABC PARSER

def parse_abc_file(file_path: str, book_number: int) -> List[Dict]:
    """
    Parse an .abc file into a list of tune dictionaries.

    Assumes tunes are separated by lines starting with 'X:' and use
    standard ABC headers like T: (title), R: (rhythm), M: (meter), K: (key).

    Args:
        file_path: Full path to the .abc file.
        book_number: Integer representing the book folder (0, 1, 2, ...).

    Returns:
        List of dicts with keys:
            book, filename, tune_ref, title, rhythm, meter, key, abc
    """
    tunes: List[Dict] = []
    filename = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.rstrip("\n") for line in f]

    current: Optional[Dict] = None
    body_lines: List[str] = []

    for line in lines:
        if line.startswith("X:"):
            # Starting a new tune
            if current is not None:
                # Save previous tune
                current["abc"] = "\n".join(body_lines)
                tunes.append(current)

            tune_ref = line[2:].strip() if len(line) > 2 else ""
            current = {
                "book": book_number,
                "filename": filename,
                "tune_ref": tune_ref,
                "title": None,
                "rhythm": None,
                "meter": None,
                "key": None,
                "abc": "",
            }
            body_lines = [line]  # start accumulating ABC body including X:

        elif current is not None:
            # Inside a tune
            body_lines.append(line)

            if line.startswith("T:") and not current["title"]:
                current["title"] = line[2:].strip()
            elif line.startswith("R:") and not current["rhythm"]:
                current["rhythm"] = line[2:].strip()
            elif line.startswith("M:") and not current["meter"]:
                current["meter"] = line[2:].strip()
            elif line.startswith("K:") and not current["key"]:
                current["key"] = line[2:].strip()

        else:
            # Lines before the first 'X:' are ignored
            continue

    # Save the last tune in file
    if current is not None:
        current["abc"] = "\n".join(body_lines)
        tunes.append(current)

    return tunes


def process_file(file_path: str, book_number: int, conn: sqlite3.Connection) -> int:
    """
    Process a single .abc file: parse tunes and insert them into the DB.

    Args:
        file_path: Path to the .abc file.
        book_number: Book number derived from directory.
        conn: Open sqlite connection.

    Returns:
        Number of tunes parsed and inserted.
    """
    tunes = parse_abc_file(file_path, book_number)
    insert_tunes(conn, tunes)
    return len(tunes)


def load_all_tunes_from_books(
    books_dir: str = BOOKS_DIR, db_path: str = DB_PATH, reset_db: bool = True
) -> None:
    """
    Walk through the abc_books directory, parse all .abc files
    and store the tunes into the database.

    Args:
        books_dir: Root folder containing numbered book folders.
        db_path: Path to the sqlite database.
        reset_db: If True, drop and recreate the tunes table before inserting.
    """
    conn = init_db(db_path, reset=reset_db)
    total_tunes = 0

    if not os.path.isdir(books_dir):
        print(f"Books directory '{books_dir}' not found.")
        conn.close()
        return

    # Iterate over directories in abc_books
    for item in os.listdir(books_dir):
        item_path = os.path.join(books_dir, item)

        # Check if it's a directory and has a numeric name
        if os.path.isdir(item_path) and item.isdigit():
            book_number = int(item)
            print(f"Found numbered directory (book): {item}")

            # Iterate over files in the numbered directory
            for file in os.listdir(item_path):
                # Check if file has .abc extension
                if file.endswith(".abc"):
                    file_path = os.path.join(item_path, file)
                    print(f"  Found abc file: {file}")
                    count = process_file(file_path, book_number, conn)
                    print(f"    Parsed & inserted {count} tune(s) from {file}")
                    total_tunes += count

    conn.close()
    print(f"\nDone. Total tunes inserted into DB: {total_tunes}")


# PANDAS DATA LOADING & ANALYSIS FUNCTIONS


def load_tunes_dataframe(db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Load all tunes from the database into a pandas DataFrame.

    Args:
        db_path: Path to the sqlite database.

    Returns:
        pandas DataFrame of tunes.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM tunes"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_tunes_by_book(df: pd.DataFrame, book_number: int) -> pd.DataFrame:
    """
    Get all tunes from a specific book.

    Args:
        df: DataFrame containing tunes.
        book_number: The book number to filter on.

    Returns:
        Filtered DataFrame of tunes in the given book.
    """
    return df[df["book"] == book_number]


def get_tunes_by_type(df: pd.DataFrame, tune_type: str) -> pd.DataFrame:
    """
    Get all tunes of a specific type/rhythm (case insensitive).

    Args:
        df: DataFrame containing tunes.
        tune_type: Tune type, e.g. 'reel', 'jig', etc.

    Returns:
        Filtered DataFrame of tunes of the given type.
    """
    if "rhythm" not in df.columns:
        return pd.DataFrame()
    return df[
        df["rhythm"].fillna("").str.lower().str.contains(tune_type.strip().lower())
    ]


def search_tunes(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """
    Search tunes by title (case insensitive).

    Args:
        df: DataFrame containing tunes.
        search_term: Text to search for in tune titles.

    Returns:
        Filtered DataFrame of tunes where the title contains the search term.
    """
    if "title" not in df.columns:
        return pd.DataFrame()
    return df[
        df["title"].fillna("").str.lower().str.contains(search_term.strip().lower())
    ]


def tunes_per_book(df: pd.DataFrame) -> pd.Series:
    """
    Return a Series with the count of tunes per book.

    Args:
        df: DataFrame containing tunes.

    Returns:
        Series indexed by book with counts of tunes.
    """
    return df.groupby("book")["id"].count().sort_index()


def most_common_keys(df: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """
    Get the most common keys in the dataset.

    Args:
        df: DataFrame containing tunes.
        top_n: Number of most common keys to return.

    Returns:
        Series of key counts.
    """
    if "key" not in df.columns:
        return pd.Series(dtype=int)
    return df["key"].value_counts().head(top_n)

# SIMPLE TEXT MENU UI

def ensure_db_populated() -> None:
    """
    Ensure the tunes table exists and is populated.
    If the table is missing or empty, parse the abc_books folder and load data.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if tunes table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tunes'"
    )
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        conn.close()
        print("Tunes table not found. Parsing ABC files and loading database...")
        load_all_tunes_from_books(BOOKS_DIR, DB_PATH, reset_db=True)
        return

    # Check if table has data
    cursor.execute("SELECT COUNT(*) FROM tunes")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        print("Tunes table is empty. Parsing ABC files and loading database...")
        load_all_tunes_from_books(BOOKS_DIR, DB_PATH, reset_db=False)


def print_tune_list(df: pd.DataFrame) -> None:
    """
    Nicely print a list of tunes with id, title, rhythm, and key.

    Args:
        df: DataFrame of tunes to print.
    """
    if df.empty:
        print("No tunes found.")
        return

    for _, row in df.iterrows():
        tune_id = row.get("id", "")
        title = row.get("title", "(no title)")
        rhythm = row.get("rhythm", "")
        key = row.get("key", "")
        print(f"[{tune_id}] {title} | {rhythm} | {key}")


def show_tune_abc(df: pd.DataFrame, tune_id: int) -> None:
    """
    Print the full ABC text for a particular tune.

    Args:
        df: DataFrame containing tunes.
        tune_id: ID of the tune to show.
    """
    tune = df[df["id"] == tune_id]
    if tune.empty:
        print(f"No tune found with id {tune_id}")
        return

    row = tune.iloc[0]
    print(f"\n--- Tune ID: {row['id']} ---")
    print(f"Title: {row['title']}")
    print(f"Book: {row['book']}")
    print(f"Rhythm: {row['rhythm']}")
    print(f"Meter: {row['meter']}")
    print(f"Key: {row['key']}")
    print("\nABC notation:\n")
    print(row["abc"])
    print("\n---------------------------\n")


def main_menu() -> None:
    """
    Main interactive menu for querying tunes.
    """
    ensure_db_populated()
    df = load_tunes_dataframe()

    while True:
        print("\n=== ABC Tunes Browser ===")
        print("1. List books and tune counts")
        print("2. Show tunes from a book")
        print("3. Show tunes by type/rhythm")
        print("4. Search tunes by title")
        print("5. Show full ABC for a tune (by id)")
        print("6. Show most common keys")
        print("0. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            counts = tunes_per_book(df)
            if counts.empty:
                print("No tunes in database.")
            else:
                print("\nTunes per book:")
                for book, count in counts.items():
                    print(f"  Book {book}: {count} tune(s)")

        elif choice == "2":
            book_str = input("Enter book number: ").strip()
            if not book_str.isdigit():
                print("Invalid book number.")
                continue
            book_number = int(book_str)
            subset = get_tunes_by_book(df, book_number)
            print_tune_list(subset)

        elif choice == "3":
            tune_type = input("Enter tune type/rhythm (e.g. reel, jig): ").strip()
            subset = get_tunes_by_type(df, tune_type)
            print_tune_list(subset)

        elif choice == "4":
            term = input("Enter text to search in tune titles: ").strip()
            subset = search_tunes(df, term)
            print_tune_list(subset)

        elif choice == "5":
            id_str = input("Enter tune id: ").strip()
            if not id_str.isdigit():
                print("Invalid id.")
                continue
            tune_id = int(id_str)
            show_tune_abc(df, tune_id)

        elif choice == "6":
            top_keys = most_common_keys(df, top_n=10)
            if top_keys.empty:
                print("No key information available.")
            else:
                print("\nMost common keys:")
                for key, count in top_keys.items():
                    print(f"  {key}: {count} tune(s)")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run the interactive menu
    main_menu()
