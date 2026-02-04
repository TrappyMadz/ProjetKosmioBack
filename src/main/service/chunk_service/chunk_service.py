from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger("chunk_service")


class ChunkService():
      def __init__(self, config):
            self.config = config

      def chunk(self, pages, size, overlap):
            # Split text in chunk
            logger.debug("Début du découpage du document...")
            splitter = RecursiveCharacterTextSplitter(chunk_size=size,
                                                      chunk_overlap=overlap,
                                                      separators=["\n\n", "\n", " "])
            if isinstance(pages, str) :
                  # Pour les questions
                  splitted_chunks = splitter.split_text(pages)
            else:
                  # Pour les documents
                  splitted_chunks = splitter.split_documents(pages)
            logger.info(f"Document découpé avec succès: {len(splitted_chunks)} chunks créés")
            return splitted_chunks



