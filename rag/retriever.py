from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from rag.vector_store import get_or_create_vector_store
from exceptions import RAGError
from config import get_settings

settings = get_settings()


def get_retriever(k: int = 3):
    """
    Returns a retriever from the vector store.
    k = number of relevant chunks to retrieve per query.
    """
    try:
        vector_store = get_or_create_vector_store()
        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    except Exception as e:
        raise RAGError(
            message="Failed to create retriever",
            details={"error": str(e)}
        )


def query_knowledge_base(question: str) -> str:
    """
    Queries the RAG knowledge base with a question.
    Returns a context-aware answer based on travel documents.
    """

    if not question:
        raise RAGError(
            message="Question cannot be empty",
            details={}
        )

    prompt_template = """You are a travel expert assistant.
Use the following context from travel documents to answer the question.
If the context doesn't contain enough information, say so clearly.
Always be helpful and specific.

Context:
{context}

Question: {input}

Answer:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "input"]
    )

    try:
        llm = ChatAnthropic(
            model=settings.model,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=1024
        )

        retriever = get_retriever(k=3)

        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

        result = retrieval_chain.invoke({"input": question})
        return result.get("answer", "")

    except Exception as e:
        raise RAGError(
            message="Failed to query knowledge base",
            details={"error": str(e)}
        )