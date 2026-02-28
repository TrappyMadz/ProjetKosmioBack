import re
from PyPDF2 import PdfReader
from model.extract_data import Extractdata
from model.process_data import ProcessData
from service.document_service.base_service import BaseService
from langchain_core.documents import Document
from config.logging_config import get_logger
import io

logger = get_logger("pdf_service")


class PdfService(BaseService):
    def __init__(self, file, config):
        self.file = file
        self.config = config

    def extract_data(self):
        #lecture des bytes du pdf
        content = self.file.file.read() 
        file_stream = io.BytesIO(content)
        reader = PdfReader(file_stream)   
        
        # On remet le curseur à zéro pour les lectures suivantes
        self.file.file.seek(0)
        
        return Extractdata(reader, 'PDF_SERVICE', self.file.filename)

    # ------------------------------------------------------------------ #
    #  Détection des pages parasites (copyright, TDM, index de figures)  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_copyright_page(text: str) -> bool:
        """Détecte les pages de mentions légales / copyright / éditeur."""
        markers = [
            "propriété intellectuelle",
            "reproduction par reprographie",
            "contrefaçon réprimée",
            "code de la propriété",
            "art. l 122",
            "toute représentation ou reproduction",
            "usage privé de copiste",
        ]
        text_lower = text.lower()
        hits = sum(1 for m in markers if m in text_lower)
        return hits >= 2  # au moins 2 marqueurs → page de copyright

    @staticmethod
    def _is_toc_or_index_page(text: str) -> bool:
        """Détecte les tables des matières et index de figures/tableaux.
        
        Heuristiques :
        - Lignes contenant des suites de points (........) suivis d'un numéro
        - Forte proportion de lignes de type "Figure XX." ou "Tableau XX."
        - Pages de type "SIGLES ET ACRONYMES", "INDEX DES TABLEAUX"
        """
        lines = text.strip().split("\n")
        if not lines:
            return False

        # Compteurs
        dotted_lines = 0      # lignes avec ........ + numéro
        figure_table_lines = 0  # lignes commençant par "Figure X" ou "Tableau X"

        for line in lines:
            stripped = line.strip()
            # Pattern : texte ......... numéro  (TDM classique)
            if re.search(r'\.{4,}\s*\d+', stripped):
                dotted_lines += 1
            # Pattern : "Figure 87." ou "Tableau 20:" en début de ligne
            if re.match(r'^(Figure|Tableau)\s+\d+', stripped, re.IGNORECASE):
                figure_table_lines += 1

        total_lines = len([l for l in lines if l.strip()])
        if total_lines == 0:
            return False

        # Si >30% des lignes sont des lignes pointillées → TDM
        if dotted_lines / total_lines > 0.3:
            return True

        # Si >40% des lignes sont des entrées Figure/Tableau → index
        if figure_table_lines / total_lines > 0.4:
            return True

        # Détection par titres de sections d'index
        text_upper = text.upper()
        index_titles = [
            "TABLE DES MATIÈRES",
            "TABLE DES MATIERES",
            "SOMMAIRE",
            "INDEX DES TABLEAUX",
            "INDEX DES FIGURES",
            "SIGLES ET ACRONYMES",
            "LISTE DES FIGURES",
            "LISTE DES TABLEAUX",
        ]
        for title in index_titles:
            if title in text_upper:
                # Vérifier que c'est bien un titre de page (pas juste une mention)
                # On vérifie que le titre est proche du début du texte
                pos = text_upper.find(title)
                if pos < 200:  # dans les 200 premiers caractères
                    return True

        return False

    @staticmethod
    def _is_references_page(text: str) -> bool:
        """Détecte les pages de bibliographie / références."""
        text_upper = text.upper()
        ref_titles = [
            "RÉFÉRENCES BIBLIOGRAPHIQUES",
            "REFERENCES BIBLIOGRAPHIQUES",
            "BIBLIOGRAPHIE",
        ]
        for title in ref_titles:
            pos = text_upper.find(title)
            if pos != -1 and pos < 100:
                return True
        
        # Heuristique : beaucoup de lignes commençant par [N]
        lines = text.strip().split("\n")
        ref_lines = sum(1 for l in lines if re.match(r'^\s*\[\d+\]', l.strip()))
        if len(lines) > 0 and ref_lines / len(lines) > 0.3:
            return True
        
        return False

    @staticmethod
    def _should_skip_page(text: str, page_num: int, total_pages: int) -> bool:
        """Décide si une page doit être exclue de l'indexation."""
        # Pages quasi-vides (couverture, pages blanches)
        if len(text.strip()) < 50:
            return True
        
        # Page de copyright
        if PdfService._is_copyright_page(text):
            return True

        # Table des matières / Index de figures
        if PdfService._is_toc_or_index_page(text):
            return True

        # Pages de références bibliographiques  
        if PdfService._is_references_page(text):
            return True

        return False

    # ------------------------------------------------------------------ #
    #  Nettoyage du texte extrait                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _clean_text(text: str) -> str:
        """Nettoie le texte extrait d'une page PDF."""
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Supprimer les lignes vides
            if not stripped:
                continue

            # Supprimer les numéros de page isolés (1-4 chiffres seuls sur une ligne)
            if re.match(r'^\d{1,4}$', stripped):
                continue

            # Supprimer les en-têtes/pieds de page récurrents type "Plan de Transition Sectoriel de l'acier : Rapport complet | 6 |"
            if re.match(r'^.*\|\s*\d+\s*\|.*$', stripped):
                continue

            # Supprimer les lignes avec uniquement des points de suite (artefacts TDM)
            if re.match(r'^[\.\s\d]+$', stripped):
                continue
            
            # Normaliser les espaces multiples
            cleaned = re.sub(r'\s{2,}', ' ', stripped)
            
            cleaned_lines.append(cleaned)

        return "\n".join(cleaned_lines)

    # ------------------------------------------------------------------ #
    #  Pipeline principal                                                  #
    # ------------------------------------------------------------------ #

    def proceed_data(self, extract_data):
        documents = []
        total_pages = len(extract_data.extract_data.pages)
        skipped_pages = []

        for i, page in enumerate(extract_data.extract_data.pages):
            text = page.extract_text()
            if not text:
                continue

            page_num = i + 1

            # Filtrage des pages parasites
            if self._should_skip_page(text, page_num, total_pages):
                skipped_pages.append(page_num)
                continue

            # Nettoyage du texte
            cleaned_text = self._clean_text(text)

            # Ne garder que les pages avec suffisamment de contenu après nettoyage
            if len(cleaned_text.strip()) < 100:
                skipped_pages.append(page_num)
                continue

            doc = Document(
                page_content=cleaned_text,
                metadata={"page": page_num}
            )
            documents.append(doc)

        if skipped_pages:
            logger.info(f"Pages filtrées ({len(skipped_pages)}): {skipped_pages}")
        logger.info(f"Pages retenues: {len(documents)}/{total_pages}")

        pdf_proceeded_service = []
    
        for doc in documents: 
            # Metadata gestion
            exclure = {'source', 'producer', 'creationdate', 'creator', 'moddate'}
            metadata = {k: v for k, v in doc.metadata.items() if k not in exclure}
            metadata['file_name']=extract_data.file_name
            metadata['count']=len(documents)
            #proceeded service gestion
            pdf_proceeded_service.append(ProcessData(doc.page_content, metadata))
        
        return pdf_proceeded_service