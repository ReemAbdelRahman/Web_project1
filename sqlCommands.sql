CREATE TABLE loginDB (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, password VARCHAR NOT NULL UNIQUE CHECK (LENGTH(password) >=4));
db.execute("SELECT EXISTS (SELECT username FROM users WHERE username =  :username)",{"username":username}")
ALTER TABLE kotob ADD COLUMN reviews json;
ALTER TABLE kotob DROP COLUMN reviews;
CREATE TABLE reviews (id SERIAL PRIMARY KEY, review json, book_isbn VARCHAR NOT NULL REFERENCES kotob(isbn));
ALTER TABLE kotob ADD CONSTRAINT constraint_name UNIQUE (isbn);
ALTER TABLE reviews ADD COLUMN user_username VARCHAR NOT NULL REFERENCES users(username);
ALTER TABLE reviews ADD CONSTRAINT change_primarykey PRIMARY KEY (book_isbn, user_username);
