from PyPDF2 import PdfReader
from model.extract_data import Extractdata
from model.process_data import ProcessData
from service.document_service.base_service import BaseService
from langchain_core.documents import Document
import io


class PdfService(BaseService):
    def __init__(self, file, config):
        self.file = file
        self.config = config

    def extract_data(self):
        # read file
        file_stream = io.BytesIO(self.file.read())
        reader = PdfReader(file_stream)   
        
        pdf_service = Extractdata(reader, 'PDF_SERVICE', self.file.filename)
        return pdf_service

    def proceed_data(self, extract_data):
        documents = []

        for i, page in enumerate(extract_data.extract_data.pages):
            text = page.extract_text()
            if text:
                doc = Document(
                    page_content=text,
                    metadata={"page": i + 1}
                )
                documents.append(doc)

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