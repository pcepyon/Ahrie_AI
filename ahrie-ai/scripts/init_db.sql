-- Ahrie AI Database Schema Initialization

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS translation_cache CASCADE;
DROP TABLE IF EXISTS halal_places CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS procedure_clinics CASCADE;
DROP TABLE IF EXISTS procedures CASCADE;
DROP TABLE IF EXISTS clinics CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'en',
    phone_number VARCHAR(50),
    email VARCHAR(255),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);

-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    chat_id INTEGER NOT NULL,
    title VARCHAR(255),
    context JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_chat_id ON conversations(chat_id);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    message_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);

-- Create clinics table
CREATE TABLE clinics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_ko VARCHAR(255),
    name_ar VARCHAR(255),
    address TEXT NOT NULL,
    district VARCHAR(100),
    phone VARCHAR(50),
    website VARCHAR(255),
    email VARCHAR(255),
    specialties TEXT[],
    languages_spoken TEXT[],
    has_female_doctors BOOLEAN DEFAULT false,
    halal_friendly BOOLEAN DEFAULT false,
    rating FLOAT,
    review_count INTEGER DEFAULT 0,
    price_range VARCHAR(50),
    business_hours JSONB,
    facilities JSONB,
    location_lat FLOAT,
    location_lng FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clinics_district ON clinics(district);
CREATE INDEX idx_clinics_specialties ON clinics USING GIN(specialties);

-- Create procedures table
CREATE TABLE procedures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_ko VARCHAR(255),
    name_ar VARCHAR(255),
    category VARCHAR(100),
    description TEXT,
    description_ko TEXT,
    description_ar TEXT,
    average_duration VARCHAR(100),
    recovery_time VARCHAR(100),
    price_range_min INTEGER,
    price_range_max INTEGER,
    popularity_score INTEGER DEFAULT 0,
    risks_and_considerations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_procedures_category ON procedures(category);

-- Create procedure_clinics junction table
CREATE TABLE procedure_clinics (
    procedure_id INTEGER REFERENCES procedures(id) ON DELETE CASCADE,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    price_min INTEGER,
    price_max INTEGER,
    waiting_time_days INTEGER,
    PRIMARY KEY (procedure_id, clinic_id)
);

-- Create reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    procedure_id INTEGER REFERENCES procedures(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    youtube_video_id VARCHAR(50),
    youtube_channel VARCHAR(255),
    language VARCHAR(10),
    sentiment_score FLOAT,
    helpful_count INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_clinic_id ON reviews(clinic_id);
CREATE INDEX idx_reviews_procedure_id ON reviews(procedure_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);

-- Create halal_places table
CREATE TABLE halal_places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    type VARCHAR(50), -- restaurant, mosque, market
    cuisine VARCHAR(100),
    address TEXT,
    district VARCHAR(100),
    phone VARCHAR(50),
    certification VARCHAR(100),
    delivery_available BOOLEAN DEFAULT false,
    price_range VARCHAR(50),
    distance_from_gangnam VARCHAR(50),
    business_hours JSONB,
    location_lat FLOAT,
    location_lng FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_halal_places_type ON halal_places(type);
CREATE INDEX idx_halal_places_district ON halal_places(district);

-- Create translation_cache table
CREATE TABLE translation_cache (
    id SERIAL PRIMARY KEY,
    source_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_translation_cache_lookup ON translation_cache(source_text, source_language, target_language);

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinics_updated_at BEFORE UPDATE ON clinics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON procedures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_halal_places_updated_at BEFORE UPDATE ON halal_places
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO procedures (name, name_ko, name_ar, category, description, average_duration, recovery_time, price_range_min, price_range_max)
VALUES 
    ('Rhinoplasty', '코성형', 'عملية تجميل الأنف', 'Facial', 'Nose reshaping surgery', '1-2 hours', '7-14 days', 3000, 8000),
    ('Double Eyelid Surgery', '쌍꺼풀 수술', 'جراحة الجفن المزدوج', 'Facial', 'Creates a crease in the upper eyelid', '30-60 minutes', '5-7 days', 1500, 3000),
    ('Facial Contouring', '안면윤곽', 'تحديد الوجه', 'Facial', 'Reshaping facial bone structure', '2-4 hours', '2-3 weeks', 7000, 15000);

INSERT INTO clinics (name, name_ko, name_ar, address, district, specialties, languages_spoken, has_female_doctors, halal_friendly, rating)
VALUES 
    ('Banobagi Plastic Surgery', '바노바기 성형외과', 'بانوباجي للجراحة التجميلية', '517 Nonhyeon-ro, Gangnam-gu, Seoul', 'Gangnam', ARRAY['Rhinoplasty', 'Facial Contouring'], ARRAY['Korean', 'English', 'Arabic'], true, true, 4.8),
    ('ID Hospital', '아이디병원', 'مستشفى آي دي', '142 Dosan-daero, Gangnam-gu, Seoul', 'Gangnam', ARRAY['All procedures'], ARRAY['Korean', 'English', 'Chinese'], true, true, 4.7);

INSERT INTO halal_places (name, name_ar, type, cuisine, address, district, certification, delivery_available, distance_from_gangnam)
VALUES 
    ('Eid Halal Korean Restaurant', 'مطعم عيد الحلال الكوري', 'restaurant', 'Korean Halal', 'Gangnam-gu, Seoul', 'Gangnam', 'KMF', true, '5-10 min'),
    ('Seoul Central Mosque', 'مسجد سيؤول المركزي', 'mosque', NULL, '39 Usadan-ro 10-gil, Yongsan-gu, Seoul', 'Itaewon', NULL, false, '30-40 min');

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;