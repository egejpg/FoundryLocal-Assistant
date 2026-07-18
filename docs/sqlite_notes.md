# SQLite Knowledge Base

## What is SQLite?
SQLite is a lightweight, serverless SQL database engine that stores an entire database in a single file on disk. It requires no separate server process or configuration, which makes it a common choice for small local applications, prototypes, and embedded storage needs.

## Opening a Connection
A connection to a SQLite database is opened with `sqlite3.connect("filename.db")` from Python's built-in `sqlite3` module. If the file does not already exist, SQLite creates it automatically; passing `":memory:"` instead of a filename creates a temporary, in-memory database that disappears when the connection closes.

## Creating a Table
Tables are created by executing a `CREATE TABLE` SQL statement through `conn.execute(...)`. Adding `IF NOT EXISTS` to the statement, as in `CREATE TABLE IF NOT EXISTS documents (...)`, prevents an error from being raised if the table has already been created in a previous run.

## Primary Keys and Autoincrement
A column declared as `INTEGER PRIMARY KEY` automatically becomes a unique row identifier, and SQLite assigns it an increasing value for each new row without needing an explicit `AUTOINCREMENT` keyword in most cases. This id column is commonly used to reference or update a specific row later.

## Inserting Data
Rows are added with an `INSERT INTO table (columns) VALUES (...)` statement. Using `?` placeholders instead of directly embedding values into the SQL string, and passing the actual values as a separate tuple to `conn.execute(...)`, protects against SQL injection and correctly handles special characters.

## Querying Data with SELECT
Reading rows uses a `SELECT` statement, for example `SELECT id, content FROM documents`. Calling `.fetchall()` on the result returns every matching row as a list of tuples, while `.fetchone()` returns just the next single row, which is useful when only one result is expected.

## Filtering with WHERE
A `WHERE` clause narrows down which rows a query returns, such as `SELECT * FROM documents WHERE id = ?`. As with inserts, using a `?` placeholder for the filter value instead of string formatting keeps the query safe from injection and correctly quoted.

## Updating and Deleting Rows
Existing rows are modified with an `UPDATE table SET column = ? WHERE condition` statement, and removed with `DELETE FROM table WHERE condition`. Leaving off the `WHERE` clause on a `DELETE` statement removes every row in the table, which is sometimes done intentionally to reset a table before reinserting fresh data.

## Transactions and Commit
Changes made through `INSERT`, `UPDATE`, or `DELETE` are not permanently saved to disk until `conn.commit()` is called. This lets multiple statements be grouped as a single unit of work; if something goes wrong before `commit()`, the changes can be rolled back instead of partially applied.

## Storing Vectors as Text
SQLite does not have a native array or vector column type, so a list of numbers like an embedding is usually converted to a string with `json.dumps(embedding)` before being inserted into a `TEXT` column. When reading it back, `json.loads(...)` converts the stored string back into a regular Python list for use in calculations.

## Closing a Connection
Calling `conn.close()` releases the database file and any associated resources once an application is done working with it. Using a `with sqlite3.connect(...) as conn:` block, or wrapping database logic in a `try/finally`, helps ensure the connection is closed even if an error occurs partway through.

## Checking Existing Tables
The special table `sqlite_master` stores metadata about every table, index, and view in a database. Querying it with `SELECT name FROM sqlite_master WHERE type='table'` lists the names of all tables currently defined, which is useful for debugging or verifying that a setup script ran correctly.

## Counting Rows
The aggregate function `COUNT(*)` returns the number of rows matching a query, for example `SELECT COUNT(*) FROM documents`. This is a quick way to confirm how many rows actually exist in a table without printing out every row's full content.

## The Database File Itself
Because a SQLite database is just a single file, it can be copied, moved, or backed up like any other file on disk. Viewing that file directly in a plain text editor is not meaningful, since it is stored in SQLite's own binary page format rather than as readable text; a proper SQL query or a dedicated SQLite browser tool should be used to inspect its contents.