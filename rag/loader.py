from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from exceptions import RAGError


DOCS_PATH = Path(__file__).parent.parent / "docs"


def load_documents() -> list:
    """
    Loads all PDF documents from the docs/ folder.
    Returns a list of chunked documents ready for embedding.
    """

    if not DOCS_PATH.exists():
        raise RAGError(
            message="docs/ folder not found",
            details={"path": str(DOCS_PATH)}
        )

    pdf_files = list(DOCS_PATH.glob("*.pdf"))

    if not pdf_files:
        raise RAGError(
            message="No PDF files found in docs/ folder",
            details={"path": str(DOCS_PATH)}
        )

    documents = []

    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            raise RAGError(
                message=f"Failed to load PDF: {pdf_path.name}",
                details={"error": str(e)}
            )

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = splitter.split_documents(documents)

    return chunks
