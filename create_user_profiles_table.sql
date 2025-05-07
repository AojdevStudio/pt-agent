-- Create user_profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INT NOT NULL,
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    fitness_level TEXT,
    goals TEXT,
    preferences TEXT
);

-- Indexes for user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_name ON public.user_profiles (name);
CREATE INDEX IF NOT EXISTS idx_user_profiles_age ON public.user_profiles (age);