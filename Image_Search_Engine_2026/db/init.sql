CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE request_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE search_history (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    username          VARCHAR(50)  NOT NULL,
    filename          VARCHAR(255) NOT NULL,
    models_used       VARCHAR(255) NOT NULL,
    dist_metric       VARCHAR(50)  NOT NULL,
    class_filter      INT          DEFAULT NULL,
    topn              INT          NOT NULL,
    result_images     JSON         NOT NULL,
    predicted_class   INT          DEFAULT NULL,
    execution_time_ms INT          NOT NULL,
    searched_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_searched_at (searched_at)
);