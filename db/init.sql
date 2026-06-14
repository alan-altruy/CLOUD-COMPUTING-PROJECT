CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE image_descriptors (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    file_hash   VARCHAR(64)  NOT NULL,
    model_name  VARCHAR(255) NOT NULL,
    descriptor  JSON         NOT NULL,
    updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_image_model (file_hash, model_name) 
);

CREATE TABLE search_history (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    username          VARCHAR(50)  NOT NULL,
    file_hash         VARCHAR(64)  NOT NULL,
    models_used       VARCHAR(255) NOT NULL,
    dist_metric       VARCHAR(50)  NOT NULL,
    class_filter      INT          DEFAULT NULL,
    topn              INT          NOT NULL,
    result_images     JSON         NOT NULL,
    predicted_class   INT          DEFAULT NULL,
    execution_time_ms INT          NOT NULL,
    searched_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_searched_at (searched_at),
    INDEX idx_file_hash (file_hash),
    UNIQUE KEY uq_search (username, file_hash, models_used, dist_metric, class_filter)
);