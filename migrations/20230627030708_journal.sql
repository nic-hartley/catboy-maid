CREATE TABLE journal (
    id INTEGER PRIMARY KEY,
    handled INTEGER NOT NULL CHECK (handled IN (0, 1)),
    content BLOB
);
