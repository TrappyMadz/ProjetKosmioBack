import argparse
import os
import pytesseract
import re
from pdf2image import convert_from_path
from typing import TypedDict, Optional
from langchain_ollama import OllamaLLM
from langgraph.graph import StateGraph, START, END
from pypdf import PdfReader

# Settings:
# Model to use to answer
llm = OllamaLLM(model="gemma:2b")

# minimum number of characters required for the pdf extraction to be considered a success.
min_extracted_char = 50

# Pdf langage in case tesseract is needed
lang='fra'

# Mode de configuration tesseract
config_tess = r'--psm 6'

# Function to get arguments :
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Treat user input with an optionnal PDF using a LLM."
    )

    parser.add_argument(
        "message",
        type=str,
        help="User input for the LLM to treat"
    )

    parser.add_argument(
        "pdf_path",
        type=str,
        nargs='?',
        default=None,
        help="Full path to PDF file to analyze (optionnal)."
    )

    args = parser.parse_args()

    if args.pdf_path is not None and not os.path.exists(args.pdf_path):
        parser.error(f"The PDF file does not exists : {args.pdf_path}")
    return args

args = parse_arguments()
user_message = args.message
pdf_path = args.pdf_path




# State initialization :
class llmState(TypedDict):
    """Represent state shared between nodes"""
    # user inputs
    user_message: str
    pdf_path: Optional[str]

    # final answer by gemma
    llm_response: Optional[str]

    # pdf content, for either pypdf or tesseract
    extracted_text: Optional[str]

    # if there is a pdf, was pypdf capable of exctracting it ?
    pypdf_success: Optional[bool]

# Nodes definition
def is_pdf(state: llmState):
    """Look if a pdf file exists and go to the next node."""
    pdf_path = state['pdf_path']

    print("Start of programm : trying to see if a pdf was sent...")
    if pdf_path is None:
        print("No pdf found, sending user message to Gemma...")
        return "generate_response"
    else:
        print("Pdf found ! Sending results to pypdf...")
        return "extract_pypdf"

def generate_response(state:llmState):
    """Generate a response. If there is a pdf, the llm works in "rag" mode"""
    user_message = state['user_message']
    extracted_text = state['extracted_text']
    
    if extracted_text and len(extracted_text.strip()) > min_extracted_char:
        print("Pdf content found ! Mini-RAG mode activated.")
        print("Generating response...")
        full_prompt = (
            f"""
        Tu es un assistant expert en analyse de documents.
        Ton rôle est de répondre à la question de l'utilisateur en te basant STRICTEMENT
        sur le CONTEXTE fourni ci-dessous.

        Règles de réponse :
        1. Utilise uniquement les informations présentes dans le CONTEXTE.
        2. Si la réponse n'est absolument pas présente dans le CONTEXTE, réponds :
           "La réponse à cette question n'est pas disponible dans le document fourni."

        CONTEXTE DU DOCUMENT :
        ---
        {extracted_text}
        ---

        QUESTION DE L'UTILISATEUR : {user_message}

        RÉPONSE :
        """
        )

        
    else:
        print("No pdf found : classic mode activated.")
        print("Generating response...")
        system_prompt = (
            "Tu es un assistant généraliste utile et amical. "
            "Réponds à la question de l'utilisateur en utilisant tes connaissances générales."
        )

        full_prompt = f"{system_prompt}\n\nQuestion : {user_message}"
        
    try:
        llm_output = llm.invoke(full_prompt)
    except Exception as e:
        llm_output = f"Fatal error when calling Gemma : {e}"
        print(f"!!!FATAL ERROR WHEN CALLING LLM: {e}")
    return {"llm_response":llm_output}

def extract_pypdf(state: llmState):
    """Try to extract text from the pdf file"""
    pdf_path = state['pdf_path']
    extracted_text = ""
    pypdf_success = False

    print("Trying to extract pdf content...")
    if not pdf_path:
        print("FATAL: pdf path missing !")
        return {"extracted_text": "", "pypdf_success":False}
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            extracted_text += page.extract_text() or ""
        if len(extracted_text.strip()) > min_extracted_char:
            pypdf_success = True
            print(f"Pdf data extracted successfuly ! {len(extracted_text.strip())} extracted caracters.")
        else:
            print("Failed to extract pdf content.")
            extracted_text = ""
    except Exception as e:
        print(f"pypdf error : {e}")
        pypdf_success = False
    return {
        "extracted_text":extracted_text,
        "pypdf_success": pypdf_success
    }

def route_extraction_success(state: llmState):
    """Determine if the extraction was successful or if a call to Tesseract is necessary."""
    if state["pypdf_success"] == True:
        return "generate_response"
    else:
        return "extract_tesseract"

def extract_tesseract(state: llmState):
    """Try to extract the content of a pdf file using Tecceract OCR"""
    pdf_path = state['pdf_path']
    extracted_text = ""
    print("Starting OCR fallback...")
    if not pdf_path:
        print("FATAL: pdf path missing !")
        return {"extracted_text": ""}
    try:
        pages = convert_from_path(pdf_path)
        config_tesseract = config_tess
        for i, image in enumerate(pages):
            page_text = pytesseract.image_to_string(image, lang=lang, config=config_tesseract)
            extracted_text += clean_ocr_text(page_text) + "\n\n"
        if len(extracted_text.strip()) > min_extracted_char:
            print(f"OCR Successfully extracted pdf data ! {len(extracted_text.strip())} characters extracted.")
        else:
            print("OCR failed to extract the pdf data. No text found.")
    except Exception as e:
        print(f"!!!FATAL ERROR WITH TESSERACT/POPPLER : {e}")
        extracted_text = ""
    return {
        "extracted_text":extracted_text,
    }

def clean_ocr_text(text: str) -> str:
    """Clean OCR text by deleting control caracters and multiple spaces"""
    cleaned_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text).strip()
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    return cleaned_text



# Nodes definition
builder = StateGraph(llmState)
builder.add_node("generate_response",generate_response)
builder.add_node("extract_pypdf",extract_pypdf)
builder.add_node("extract_tesseract", extract_tesseract)

# Routes Definition
builder.add_conditional_edges(
    START,
    is_pdf,
    {
        "generate_response":"generate_response",
        "extract_pypdf":"extract_pypdf",
    }
)
builder.add_edge("generate_response",END)
builder.add_conditional_edges(
    "extract_pypdf",
    route_extraction_success,
    {
        "generate_response":"generate_response",
        "extract_tesseract":"extract_tesseract",
    }
)
builder.add_edge("extract_tesseract","generate_response")


graph = builder.compile()

# Graph visualization !
png_data = graph.get_graph().draw_mermaid_png()
output_filename = "langgraph_workflow.png"
try:
    with open(output_filename, "wb") as f:
        f.write(png_data)
except Exception as e:
    print("ERREUR")

# invoke it :
result = graph.invoke({
    "user_message":user_message,
    "pdf_path": pdf_path,
    "extracted_text": None,
    "llm_response": None,
    "pypdf_success":None,
})


print(f"Your request : {result['user_message']}")
print(f"Pdf path : {result['pdf_path']}")
print(f"Llm answer : {result['llm_response']}")
