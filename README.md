# Data Centric Programming Assignment 2025
# Name: Titas Utyra
# Student Number: C24448002
# Lectured And Mentored By: Dr.Brian Duggan

# Description of the Project:
This project implements a complete end to end Python application for loading, parsing, analysing, and querying ABC music notation files sourced from multiple folders (“abc_books”).
The aim is to demonstrate core competencies in file parsing, database management, pandas based analysis, and building an interactive data centric application with proper version control.

<img width="1130" height="733" alt="image" src="https://github.com/user-attachments/assets/b2e0a2d9-ec27-4408-b42e-1af18ec27a7a" />

<img width="998" height="310" alt="image" src="https://github.com/user-attachments/assets/d13b9387-bf36-4a34-8535-493c3ee55521" />


# The program:
Recursively loads .abc files from abc_books/<book_number>/.
Parses all tunes inside each file into structured Python dictionaries.
Stores the tune metadata and full ABC notation into an SQLite database.
Loads the database into a pandas DataFrame for easy analysis.
Provides an interactive menu based user interface for querying tunes.

<img width="296" height="160" alt="image" src="https://github.com/user-attachments/assets/5d3abf80-8ce3-41ee-99ec-69b301b27a35" />

# Includes analysis utilities such as:
Tunes per book.
Tunes by type/rhythm.
Searching by title.


# On first run, if tunes.db does not exist, the system:
Parses all files,
Extracts all tune metadata,
Saves everything to an SQLite database.

# Use the interactive menu to:
View books and tune counts,
Browse tunes by book,
Filter by rhythm/type (e.g., “reel”, “jig”),
Search by title text,
Display full ABC notation for any tune,
View most common musical keys,
Re-run anytime — the database will load instantly unless empty.

# How It Works:
1. File Traversal
The program walks through the abc_books/ directory.
Each numeric folder (0, 1, 2, …) is treated as a “book”.

2. ABC Parsing
Each .abc file may contain multiple tunes.

A tune begins with X: and may include:
T: Title
R: Rhythm / tune type
M: Meter
K: Key

3. SQLite Storage

A table tunes is created with:

Column	Description
id	Auto-increment primary key
book	Book number
filename	Source file name
tune_ref	X: reference number
title	T: title
rhythm	R: tune type
meter	M: meter signature
key	K: key signature
abc	Entire ABC body

4. Loading With pandas
A utility loads all database rows into a DataFrame:
df = pd.read_sql("SELECT * FROM tunes", conn)

5. Analysis Functions
Tunes by book
get_tunes_by_book(df, book_number)
Tunes by rhythm/type
get_tunes_by_type(df, tune_type)
Search by title
search_tunes(df, search_term)
Most common keys
Uses value_counts() to find popular key signatures.

6. Interactive Menu
A simple text-based interface lets users:
Explore all books
Filter tunes
Search titles
Open any tune and view the full ABC notation

# List of Files in the Project:
main.py	
abc_books/	Provided dataset folders
tunes.db	Generated automatically
README.md	

# References:
ABC notation specification — https://abcnotation.com/wiki/abc:standard:v2.1
Python SQLite documentation — https://docs.python.org/3/library/sqlite3.html


# What I Am Most Proud Of in the Assignment:
I am most proud of building a fully working end to end data pipeline.
Automated parsing of multiple tune ABC files.
Clean separation between parsing, database storage, and analysis.
Building a full interactive menu system.
The final result feels like a real mini app, not just coursework.

# What I Learned:
Recursive file system traversal.
Designing relational database tables around real world data.
Managing CRUD operations with SQLite.
Using version control (Git & GitHub)
