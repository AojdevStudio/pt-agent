-- Create knowledge_base table
CREATE TABLE IF NOT EXISTS public.knowledge_base (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding FLOAT[] DEFAULT '{}',
    category TEXT,
    source TEXT,
    date_added DATE
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_base_title ON public.knowledge_base (title);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON public.knowledge_base (category);
