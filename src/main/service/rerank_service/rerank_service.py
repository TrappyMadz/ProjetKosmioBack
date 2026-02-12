from flashrank import Ranker, RerankRequest
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger("rerank_service")


class ReRankService:
    def __init__(self):
        logger.info("Chargement du modèle de re-ranking FlashRank...")
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
        logger.info("Modèle de re-ranking chargé avec succès")

    def rerank(self, query: str, documents: list, metadatas: list, top_k: int = 5) -> tuple:
        """
        Re-classe les documents par pertinence réelle via un cross-encoder.

        Args:
            query: La question/description textuelle du champ recherché
            documents: Liste de textes (chunks) récupérés par la recherche vectorielle
            metadatas: Liste de métadonnées associées aux documents
            top_k: Nombre de résultats à garder après re-ranking

        Returns:
            Tuple (documents_reranked, metadatas_reranked) triés par pertinence décroissante
        """
        if not documents:
            return [], []

        # Créer les passages pour FlashRank
        passages = [{"id": str(i), "text": doc} for i, doc in enumerate(documents)]

        # Lancer le re-ranking
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # Extraire les top_k résultats triés par score décroissant
        reranked_docs = []
        reranked_metas = []
        for result in results[:top_k]:
            idx = int(result["id"])
            reranked_docs.append(documents[idx])
            reranked_metas.append(metadatas[idx])
            logger.debug(f"Re-rank: score={result['score']:.4f} pour chunk idx={idx}")

        logger.info(f"Re-ranking terminé: {len(documents)} → {len(reranked_docs)} documents (top_k={top_k})")
        return reranked_docs, reranked_metas
