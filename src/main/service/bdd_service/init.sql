-- Création de la table initiale
CREATE TABLE  IF NOT EXISTS fiche_en_json (
                type VARCHAR (50) NOT NULL,
                id SERIAL PRIMARY KEY,
                title VARCHAR (500),
                metadata JSONB,
                summary TEXT,
                content JSONB,
                contribution JSONB,
                traceability JSONB, 
                file_version INTEGER DEFAULT 1
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
    file_version INTEGER,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logique de d'archivage : quand on modifie une fiche dans la table principale, on stock d'abord sont contenue dans la table d'historique
CREATE OR REPLACE FUNCTION archive_before_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Sauvegarde de l'ancienne version
    INSERT INTO fiche_en_json_history (
        fiche_id, type, title, metadata, summary, content, contribution, traceability, file_version
    )
    VALUES (
        OLD.id, OLD.type, OLD.title ,OLD.metadata, OLD.summary, OLD.content, OLD.contribution, OLD.traceability, OLD.file_version
    );

    NEW.file_version = OLD.file_version +1;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du déclancheur (quand la fonction sera appelée ?)
DROP TRIGGER IF EXISTS trigger_archive_fiche ON fiche_en_json;
CREATE TRIGGER trigger_archive_fiche
BEFORE UPDATE ON fiche_en_json
FOR EACH ROW
EXECUTE FUNCTION archive_before_update();