CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    avatar BLOB DEFAULT NULL,
    time integer NOT NULL
);