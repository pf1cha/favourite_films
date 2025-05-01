CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    imdb_id VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    year VARCHAR(20),
    type VARCHAR(50),
    poster_url TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_user_movie UNIQUE (user_id, imdb_id)
);
