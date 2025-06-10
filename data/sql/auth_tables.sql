-- Table des utilisateurs authentifiés
CREATE TABLE IF NOT EXISTS auth_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}',
    favorite_genres TEXT[],
    reading_history JSONB DEFAULT '[]',
    profile_image_url VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user'
);

-- Index pour améliorer les performances des recherches
CREATE INDEX IF NOT EXISTS idx_auth_users_username ON auth_users(username);
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_users(email);
CREATE INDEX IF NOT EXISTS idx_auth_users_favorite_genres ON auth_users USING GIN(favorite_genres);

-- Table des sessions utilisateurs pour la gestion de la persistance de connexion
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    data JSONB DEFAULT '{}'
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at); 