DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS Hashtags;
DROP TABLE IF EXISTS Subscriptions;


-- CREATE TYPE Privileges AS ENUM ('guest', 'user', 'moder', 'admin');

CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO Users (login, password, privilege)
VALUES ('admin', crypt('admin', gen_salt('md5')), '2');

CREATE TABLE IF NOT EXISTS Users
(
    id       SERIAL PRIMARY KEY,
    login    VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    privilege     VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS Posts
(
    post_id SERIAL PRIMARY KEY,
    user_id int  NOT NULL,
    post    text NOT NULL,
    time    timestamp DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Hashtags
(
    ht_id   SERIAL PRIMARY KEY,
    post_id int  NOT NULL,
    hashtag text NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Posts (post_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Subscriptions
(
    id_from SERIAL PRIMARY KEY,
    id_to   int NOT NULL,
    FOREIGN KEY (id_from) REFERENCES Users (id) ON DELETE CASCADE ON UPDATE CASCADE
);


SELECT *
FROM Users;

SELECT *
FROM Hashtags;

SELECT *
FROM Posts;

SELECT *
FROM Subscriptions;

