CREATE TABLE  IF NOT EXISTS fiche_en_json (
                type VARCHAR (50) NOT NULL,
                id SERIAL PRIMARY KEY,
                title VARCHAR (500),
                metadata JSONB,
                summary TEXT,
                content JSONB,
                contribution JSONB,
                traceability JSONB );

CREATE TABLE IF NOT EXISTS qualimetrie_retour_llm (
    id SERIAL PRIMARY KEY,
    id_retour INTEGER NOT NULL,
    completion FLOAT,
    confiance_globale FLOAT
);

ALTER TABLE qualimetrie_retour_llm
ADD CONSTRAINT IF NOT EXISTS fk_qualimetrie_fiche
FOREIGN KEY (id_retour)
REFERENCES fiche_en_json(id)
ON DELETE CASCADE;