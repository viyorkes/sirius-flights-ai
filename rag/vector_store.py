from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from exceptions import RAGError

VECTOR_STORE_PATH = Path(__file__).parent.parent / "data" / "vector_store"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vector_store(chunks: list) -> FAISS:
    if not chunks:
        raise RAGError(
            message="No chunks provided to create vector store",
            details={}
        )
    try:
        embeddings = get_embeddings()
        vector_store = FAISS.from_documents(chunks, embeddings)
        VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(VECTOR_STORE_PATH))
        return vector_store
    except Exception as e:
        raise RAGError(
            message="Failed to create vector store",
            details={"error": str(e)}
        )


def load_vector_store() -> FAISS:
    if not VECTOR_STORE_PATH.exists():
        raise RAGError(
            message="Vector store not found. Run create_vector_store first.",
            details={"path": str(VECTOR_STORE_PATH)}
        )
    try:
        embeddings = get_embeddings()
        vector_store = FAISS.load_local(
            str(VECTOR_STORE_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_store
    except Exception as e:
        raise RAGError(
            message="Failed to load vector store",
            details={"error": str(e)}
        )


def get_or_create_vector_store(chunks: list = None) -> FAISS:
    if VECTOR_STORE_PATH.exists():
        return load_vector_store()
    if not chunks:
        raise RAGError(
            message="No vector store found and no chunks provided",
            details={}
        )
    return create_vector_store(chunks)