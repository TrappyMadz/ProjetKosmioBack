CREATE TABLE  IF NOT EXISTS fiche_en_json (
                type VARCHAR (50) NOT NULL,
                id SERIAL PRIMARY KEY,
                title VARCHAR (500),
                metadata JSONB,
                summary TEXT,
                content JSONB,
                contribution JSONB,
                traceability JSONB );