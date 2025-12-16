# ajout d'élements dans la base de données et création de la base de données
import psycopg2
from psycopg2.extras import Json, RealDictCursor
import os

class PostgresService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _get_connection(self):
        """
        Fonction permettant de se connecter à la bdd.
        Retourne la connexion si tout fonctionne, None sinon.
        """
        try:
            return psycopg2.connect(self.db_url)
        except Exception as exception:
            print(f"Erreur de connexion à la BDD : {exception}")
            return None

    # ---Fonction CREATE---
    def insert_new_fiche(self, data):
        """
        Insère une nouvelle fiche JSON complète dans la base de donnée.
        data doit être un dictionnaire contenant : type, title, metadata, summary, content, contribution et traceability
        Retourne l'id si tous ses bien passé, none sinon
        """
        connection = self._get_connection()
        if not connection: return None
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
                print(f"Fiche créer avec ID : {new_id}")
                return new_id
        except Exception as exception:
            connection.rollback()
            print(f"Erreur lor de la création de la fiche : {exception}")
            return None
        finally:
            connection.close()

    # ---Fonction READALL---
    def get_all_fiches(self):
        """
        Récupère toutes les fiches. Retourne None si il y a eu un problème, un tableau contenant toutes les fiches sinon
        """
        connection = self._get_connection()
        if not connection: return None
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json;")
                return cursor.fetchall()
        except Exception as exception:
            print(f"Erreur lor de la lecture des fiches : {exception}")
            return None
        finally:
            connection.close() 

     # ---Fonction READONE---
    def get_fiche_by_id(self, id):
        """
        Récupère la fiche d'id "id". Retourne None si il y a eu un problème, un tableau contenant la fiche sinon
        """
        connection = self._get_connection()
        if not connection: return None
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM fiche_en_json WHERE id = %s;", (id, ))
                return cursor.fetchone()
        except Exception as exception:
            print(f"Erreur lor de la lecture de la fiche {id} : {exception}")
            return None
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
            "use_cases": [
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