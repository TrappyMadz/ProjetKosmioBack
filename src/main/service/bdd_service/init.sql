CREATE TABLE  IF NOT EXISTS fiche_en_json (
                type VARCHAR (50) NOT NULL,
                id SERIAL PRIMARY KEY,
                title VARCHAR (500),
                metadata JSONB,
                summary TEXT,
                content JSONB,
                contribution JSONB,
                traceability JSONB, 
                images JSONB DEFAULT '{}',
                file_version INTEGER DEFAULT 1
);

-- Table pivot pour les images (Lien entre PostgreSQL et MinIO)
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id SERIAL PRIMARY KEY,
    fiche_id INTEGER NOT NULL REFERENCES fiche_en_json(id) ON DELETE CASCADE,
    file_key TEXT NOT NULL,       -- Identifiant unique dans le bucket
    bucket_name VARCHAR(50) NOT NULL DEFAULT 'fiches-images',
    file_name VARCHAR(255),       -- Nom d'origine du fichier
    content_type VARCHAR(50),     -- Type MIME (image/png, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes de récupération d'images
CREATE INDEX IF NOT EXISTS idx_attachments_fiche_id ON attachments(fiche_id);


CREATE TABLE IF NOT EXISTS qualimetrie_retour_llm (
    id SERIAL PRIMARY KEY,
    id_retour INTEGER NOT NULL,
    completion FLOAT,
    confiance_globale FLOAT
);



-- Création de la table contenant l'historique des versions. Si un fichier est supprimé dans la table principale, toutes ses verisons sont supprimés automatiquement.
CREATE TABLE IF NOT EXISTS fiche_en_json_history (
    history_id SERIAL PRIMARY KEY,
    fiche_id INTEGER REFERENCES fiche_en_json(id) ON DELETE CASCADE,
    type VARCHAR (50) NOT NULL,
    title VARCHAR (500),
    metadata JSONB,
    summary TEXT,
    content JSONB,
    contribution JSONB,
    traceability JSONB ,
    images JSONB DEFAULT '{}',
    file_version INTEGER,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logique de d'archivage : quand on modifie une fiche dans la table principale, on stock d'abord sont contenue dans la table d'historique
CREATE OR REPLACE FUNCTION archive_before_update()
RETURNS TRIGGER AS $$
BEGIN
    -- On vérifie si le contenu textuel/structurel a réellement changé
    -- On utilise 'IS NOT DISTINCT FROM' pour gérer correctement les valeurs NULL
    IF (
        OLD.type IS NOT DISTINCT FROM NEW.type AND
        OLD.title IS NOT DISTINCT FROM NEW.title AND
        OLD.metadata IS NOT DISTINCT FROM NEW.metadata AND
        OLD.summary IS NOT DISTINCT FROM NEW.summary AND
        OLD.content IS NOT DISTINCT FROM NEW.content AND
        OLD.contribution IS NOT DISTINCT FROM NEW.contribution AND
        OLD.traceability IS NOT DISTINCT FROM NEW.traceability
    ) THEN
        -- Si SEULES les images (ou la version) ont changé :
        -- On ne fait pas d'insertion dans l'historique et on n'incrémente pas file_version
        RETURN NEW;
    END IF;

    -- Sinon (vrai changement de contenu), on archive l'ancienne version
    INSERT INTO fiche_en_json_history (
        fiche_id, type, title, metadata, summary, content, contribution, traceability, images, file_version
    )
    VALUES (
        OLD.id, OLD.type, OLD.title, OLD.metadata, OLD.summary, OLD.content, OLD.contribution, OLD.traceability, OLD.images, OLD.file_version
    );

    -- On incrémente la version uniquement pour les changements de contenu
    NEW.file_version = OLD.file_version + 1;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du déclancheur (quand la fonction sera appelée ?)
DROP TRIGGER IF EXISTS trigger_archive_fiche ON fiche_en_json;
CREATE TRIGGER trigger_archive_fiche
BEFORE UPDATE ON fiche_en_json
FOR EACH ROW
EXECUTE FUNCTION archive_before_update();