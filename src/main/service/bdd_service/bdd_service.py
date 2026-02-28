# ajout d'élements dans la base de données et création de la base de données
import psycopg2
from psycopg2.extras import Json, RealDictCursor
import os
import json
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger(__name__)

class PostgresService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _get_connection(self):
        """
        Fonction permettant de se connecter à la bdd.
        Retourne la connexion si tout fonctionne, Raise une exception sinon
        """
        try:
            return psycopg2.connect(self.db_url)
        except Exception as exception:
            logger.error(f"Erreur de connexion à la BDD: {exception}")
            raise exception

    def check_fiche_exists(self, fiche_id):
        """Vérifie rapidement si une fiche existe."""
        connection = self._get_connection()
        if not connection: return False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM fiche_en_json WHERE id = %s;", (fiche_id,))
                return cursor.fetchone() is not None
        finally:
            connection.close()

    # ---Fonction CREATE---
    def insert_new_fiche(self, data):
        """
        Insère une nouvelle fiche JSON complète dans la base de donnée.
        data doit être un dictionnaire contenant : type, title, metadata, summary, content, contribution et traceability
        Retourne l'id si tous ses bien passé, peut raise une exception si la connexion échoue ou si l'insertion échoue.
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                INSERT INTO fiche_en_json
                (type, title, metadata, summary, content, contribution, traceability)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                # On utilisera Json() pour convertir les dictionnaires python en Json
                cursor.execute(query, (
                    data.get("type"),
                    data.get("title"),
                    Json(data.get("metadata", {})),
                    data.get("summary"),
                    Json(data.get("content", {})),
                    Json(data.get("contribution", {})),
                    Json(data.get("traceability", {}))
                ))
                new_id = cursor.fetchone()[0]
                connection.commit()
                logger.info(f"Fiche créée avec ID: {new_id}")
                return new_id
        except Exception as exception:
            connection.rollback()
            logger.error(f"Erreur lors de l'insertion de la fiche: {exception}")
            raise exception
        finally:
            connection.close()

    # ---Fonction READALL--- NE PAS UTILISER
    def _get_all_fiches_by_type(self, fiche_type):
        """
        Récupère toutes les fiches. Retourne un tableau contenant toutes les fiches d'un certain type et raise une exception si la connexion ou la requête échoue.
        """
        connection = self._get_connection()
        if not connection:
            raise Exception("Impossible de se connecter à la bdd")
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json WHERE type = %s;", (fiche_type,))
                fiches = cursor.fetchall()
                for fiche in fiches:
                    for col in ['metadata', 'content', 'contribution', 'traceability']:
                        if isinstance(fiche.get(col), str):
                            fiche[col] = json.loads(fiche[col])
                return fiches
        except Exception as exception:
            logger.error(f"Erreur lors de la lecture des fiches de type {fiche_type}: {exception}")
            raise exception
        finally:
            connection.close() 

    # FONCTIONS READALL PAR TYPE -> UTILISER CELLES-CI 
    def get_all_solutions(self):
        """Récupère toutes les fiches de type solution."""
        return self._get_all_fiches_by_type("solution")

    def get_all_sectors(self):
        """Récupère toutes les fiches de type secteur."""
        return self._get_all_fiches_by_type("sector")

     # ---Fonction READONE---
    def get_fiche_by_id(self, id):
        """
        Récupère la fiche d'id "id". Retourne un dictionnaire unique contenant la fiche, None si la fiche n'existe pas, et raise une exception si la connection ou la lecture échoue
        """
        connection = self._get_connection()
        if not connection:
            raise Exception("Impossible de se connecter à la bdd")
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json WHERE id = %s;", (id, ))
                fiche = cursor.fetchone()

                if fiche:
                    for col in ['metadata', 'content', 'contribution', 'traceability']:
                        if isinstance(fiche.get(col), str):
                            fiche[col] = json.loads(fiche[col])
                return fiche
        except Exception as exception:
            logger.error(f"Erreur lors de la lecture de la fiche {id}: {exception}")
            raise exception
        finally:
            connection.close() 
    
    # ---Fonction READALLARCHIVED---
    def get_all_fiche_history(self):
        """
        Récupère toutes les fiches contenus dans les archives. Retourne un tableau contenant toutes les fiches et raise une exception si la connexion ou la requête échoue.
        """
        connection = self._get_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json_history;")
                return cursor.fetchall()
        except Exception as exception:
            logger.error(f"Erreur lors de la lecture de l'historique des fiches: {exception}")
            raise exception
        finally:
            connection.close() 

    #---Fonction READONEARCHIVED---
    def get_one_fiche_history(self, id):
        """
        Récupère l'historique des modifs de la fiche d'id "id". Retourne un tableau contenant les fiches, None si la fiche n'existe pas, et raise une exception si la connection ou la lecture échoue
        """
        connection = self._get_connection()
        if not connection: return None
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json_history WHERE fiche_id = %s;", (id, ))
                return cursor.fetchall()
        except Exception as exception:
            logger.error(f"Erreur lors de la lecture de l'historique de la fiche {id}: {exception}")
            return -1
        finally:
            connection.close() 
    

    # ---Fonction FULLUPDATE---
    def update_fiche(self, id, data):
        """
        Met à jour une fiche existante. Cette fonction remplace TOUTES les données.
        Retourne l'id de la fiche en cas de réussite, None si la fiche n'existe pas, et soulève une exception si la connexion échoue ou si l'update échoue
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                query = """
                UPDATE fiche_en_json
                SET type = %s,
                    title = %s,
                    metadata = %s,
                    summary = %s,
                    content = %s,
                    contribution = %s,
                    traceability = %s
                WHERE id = %s;
                """

                cursor.execute(query, (
                    data.get("type"),
                    data.get("title"),
                    Json(data.get("metadata", {})),
                    data.get("summary"),
                    Json(data.get("content", {})),
                    Json(data.get("contribution", {})),
                    Json(data.get("traceability", {})),
                    id
                ))
                connection.commit()

                # On vérifie que la mise à jour à fonctionnée (rowcount définie le nombre de lignes modifiées)
                if cursor.rowcount > 0:
                    logger.info(f"Fiche {id} mise à jour avec succès")
                    return id
                else:
                    logger.warning(f"Aucune fiche trouvée avec l'id {id}")
                    return None
        except Exception as exception:
            connection.rollback()
            logger.error(f"Erreur pendant l'update de la fiche {id}: {exception}")
            raise exception
        finally:
            connection.close()

    def delete_fiche(self, id):
        """
        Supprime la fiche avec l'id id. Renvoie l'id si la supression s'est bien passée, None si l'id n'existait pas, et soulève une exception si la connexion
        à la base de donnée échoue ou si il y a un autre problème.
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query= "DELETE FROM fiche_en_json WHERE id = %s;"
                cursor.execute(query, (id,))
                connection.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Fiche {id} supprimée avec succès")
                    return id
                else:
                    logger.warning(f"Aucune fiche trouvée avec l'id {id}")
                    return None
        except Exception as exception:
            connection.rollback()
            logger.error(f"Erreur de suppression de la fiche {id}: {exception}")
            raise exception
        finally:
            connection.close()

    def get_attachment_by_id(self, attachment_id):
        """Récupère les métadonnées de l'image (clé et type) pour l'affichage."""
        connection = self._get_connection()
        if not connection: return None
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # On récupère file_key et content_type
                query = "SELECT file_key, content_type FROM attachments WHERE attachment_id = %s;"
                cursor.execute(query, (attachment_id,))
                return cursor.fetchone()
        finally:
            connection.close()


    def save_attachment_and_update_fiche(self, fiche_id, file_key, section, file_name, content_type):
        """
        Enregistre l'image dans 'attachments' et met à jour le champ 'images' de la fiche.
        """
        connection = self._get_connection()
        if not connection: return None
        
        try:
            with connection.cursor() as cursor:
                # On insère dans la table attachments
                query_attachment = """
                    INSERT INTO attachments (fiche_id, file_key, bucket_name, file_name, content_type)
                    VALUES (%s, %s, %s, %s, %s) RETURNING attachment_id;
                """
                cursor.execute(query_attachment, (fiche_id, file_key, "fiches-images", file_name, content_type))
                new_attachment_id = cursor.fetchone()[0]

                # On met à jour le JSONB 'images' de la fiche
                # On utilise jsonb_set pour ajouter l'ID dans la bonne section du dictionnaire
                query_update_fiche = f"""
                    UPDATE fiche_en_json 
                    SET images = jsonb_set(
                        COALESCE(images, '{{}}'), 
                        '{{{section}}}', 
                        COALESCE(images->'{section}', '[]'::jsonb) || TO_JSONB(%s::int)
                    )
                    WHERE id = %s;
                """
                cursor.execute(query_update_fiche, (new_attachment_id, fiche_id))
                
                connection.commit()
                return new_attachment_id
        except Exception as e:
            connection.rollback()
            logger.error(f"Erreur traçabilité image : {e}")
            return None
        finally:
            connection.close()

    def delete_image_logic(self, id_fiche, id_img):
        connection = self._get_connection()
        if not connection: return None
        file_key_to_delete = None

        try:
            with connection.cursor() as cursor:
                # Retrait de l'ID de la fiche actuelle
                query_remove = """
                    UPDATE fiche_en_json
                    SET images = (
                        SELECT jsonb_object_agg(key, (
                            SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb)
                            FROM jsonb_array_elements(val) AS elem
                            WHERE elem::int != %s
                        ))
                        FROM jsonb_each(images) AS sections(key, val)
                    )
                    WHERE id = %s;
                """
                cursor.execute(query_remove, (id_img, id_fiche))

                # VÉRIFICATION CIBLÉE : On ne regarde QUE l'historique de CETTE fiche
                # On vérifie si l'ID de l'image est encore présent dans les archives de 'id_fiche'
                check_history_query = """
                    SELECT EXISTS (
                        SELECT 1 FROM fiche_en_json_history 
                        WHERE fiche_id = %s 
                        AND images @@ ('$.* == ' || %s)::jsonpath
                    );
                """
                cursor.execute(check_history_query, (id_fiche, id_img))
                is_still_in_history = cursor.fetchone()[0]

                # Suppression si l'historique de cette fiche n'en a plus besoin
                if not is_still_in_history:
                    # On récupère la clé pour MinIO avant de supprimer la ligne
                    cursor.execute("SELECT file_key FROM attachments WHERE attachment_id = %s;", (id_img,))
                    res = cursor.fetchone()
                    if res:
                        file_key_to_delete = res[0]
                        cursor.execute("DELETE FROM attachments WHERE attachment_id = %s;", (id_img,))

                connection.commit()
                return file_key_to_delete # Retourne la clé si on doit supprimer dans MinIO
                
        except Exception as e:
            connection.rollback()
            logger.error(f"Erreur suppression image : {e}")
            return False
        finally:
            connection.close()




    ###### Qualimetrie ######




    def add_qualimetrie(self, id, qualimetrie):
        """
        ajout qualimétrie
        """
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                INSERT INTO qualimetrie_retour_llm
                (id_retour, completion, confiance_globale)
                VALUES (%s, %s, %s)
                RETURNING id;
                """
                # On utilisera Json() pour convertir les dictionnaires python en Json
                cursor.execute(query, (
                    id,
                    qualimetrie["completion"],
                    qualimetrie["confiance"]
                ))
                new_id = cursor.fetchone()[0]
                connection.commit()
                print(f"Qualimétrie ajoutée avec ID : {new_id}")
                return new_id
        except Exception as exception:
            connection.rollback()
            print(f"Erreur lecture SQL : {exception}")
            raise exception
        finally:
            connection.close()





## pour tester faire bdd_service.test() dans run.py
def test():
    exemple = {
        "type": "secteur",
        "id": "sec_98765",
        "title": "Industrie Agroalimentaire",
        "metadata": {
            "sub_sectors": [
                "Laiterie",
                "Plats préparés",
                "Boissons",
                "Boulangerie industrielle"
            ],
            "company_size": "PME / ETI",
            "last_update": "2025-11-20",
            "contributors": [
                "Groupe de travail IAA",
                "CITEPA"
            ]
        },
        "summary": "Le secteur agroalimentaire transforme des produits agricoles en aliments. Il est caractérisé par des besoins importants en chaleur (cuisson, pasteurisation) et en froid (conservation).",
        "content": {
            "description": "Avec plus de 15 000 entreprises en France, l'IAA est le premier secteur industriel. Les contraintes sanitaires et la gestion de la chaîne du froid sont structurantes pour la consommation énergétique.",
            "emissions_profile": {
                "process": "60% (Cuisson, évaporation, séchage)",
                "utilities": "25% (Froid industriel, air comprimé, vapeur)",
                "building": "5% (Chauffage locaux, éclairage)",
                "transport": "8% (Logistique aval)",
                "waste": "2% (Effluents)"
            },
            "challenges": [
                {
                    "title": "Décarbonation de la chaleur",
                    "description": "Sortir des chaudières gaz pour la production de vapeur et d'eau chaude."
                },
                {
                    "title": "Fluides frigorigènes",
                    "description": "Remplacement des HFC à fort GWP par des fluides naturels (NH3, CO2, Propane)."
                }
            ],
            "regulations": [
                "Décret Tertiaire (pour les sièges et entrepôts)",
                "F-Gas (Froid)",
                "Quota CO2 (sites ETS)"
            ],
            "systems_matrix": [
                {
                    "system": "Production de froid",
                    "impact": "Moyen à Fort",
                    "priority": "⭐⭐⭐",
                    "solutions": [
                        "HP Flottante",
                        "Récupération de chaleur sur groupes froid",
                        "Free-cooling"
                    ]
                },
                {
                    "system": "Production de vapeur",
                    "impact": "Très Fort",
                    "priority": "⭐⭐⭐",
                    "solutions": [
                        "Chaudière Biomasse",
                        "Pompes à chaleur HT",
                        "Électrification"
                    ]
                },
                {
                    "system": "Air comprimé",
                    "impact": "Faible",
                    "priority": "⭐",
                    "solutions": [
                        "Variation de vitesse",
                        "Détection de fuites"
                    ]
                }
            ],
            "sector_path": [
                {
                    "phase": "Quick wins (< 3 mois)",
                    "action": "Pilotage énergétique, calorifugeage des réseaux, réparation des fuites d'air/vapeur."
                },
                {
                    "phase": "Optimisations (3–12 mois)",
                    "action": "Mise en place de HP flottante, récupération de chaleur fatale simple."
                },
                {
                    "phase": "Investissements structurants",
                    "action": "Installation de PAC industrielles, chaudière biomasse."
                },
                {
                    "phase": "Nouvelles énergies / changement de combustible",
                    "action": "Substitution gaz par biomasse ou électrification des procédés."
                },
                {
                    "phase": "Management & pilotage",
                    "action": "Certification ISO 50001 et mise en place d'un système de management de l'énergie (SME)."
                }
            ],
            "use_case": [
                {
                    "sub_sector": "Laiterie",
                    "actions": "Installation d'une PAC sur les buées de séchage.",
                    "results": "-40% de consommation gaz.",
                    "link": "https://wikico2.org/projet/dairy-hp"
                },
                {
                    "sub_sector": "Boulangerie",
                    "actions": "Récupération de chaleur sur fours pour ECS.",
                    "results": "Autonomie eau chaude nettoyage.",
                    "link": ""
                }
            ],
            "resources": [
                {
                    "title": "Guide ADEME - Efficacité énergétique en IAA",
                    "type": "Guide technique",
                    "link": "https://example.com/guide-ademe"
                },
                {
                    "title": "Bref Clean Technologies",
                    "type": "Réglementaire",
                    "link": "https://example.com/bref-clean-tech"
                }
            ]
        },
        "contribution": {
            "completeness": "Complète",
            "validator": "Jean Dupont (Expert Sectoriel)",
            "history": [
                "2025-11-20: Validation finale",
                "2025-01-10: Création initiale"
            ],
            "improvement_proposal_link": "https://wikico2.org/feedback/sec_98765"
        },
        "traceability": {
            "source_pdf": "Etude_Sectorielle_IAA_2024.pdf",
            "extraction_confidence": 0.88,
            "chunks_used": [
                "chk_101",
                "chk_102",
                "chk_table_3"
            ]
        }
    }

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))


    cur = conn.cursor()


    cur.execute(
        "INSERT INTO fiche_en_json (type, title, metadata, summary, content, contribution, traceability) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (exemple["type"], exemple["title"], Json(exemple["metadata"]), exemple["summary"], Json(exemple["content"]), Json(exemple["contribution"]), Json(exemple["traceability"])))


    conn.commit()
    cur.close()
    conn.close()
    print("Donnée insérée avec succès.")
