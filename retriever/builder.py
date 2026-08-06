from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from config.settings import settings
import logging
import os

logger = logging.getLogger(__name__)


class RetrieverBuilder:

    def __init__(self):
        """
        Initialize retriever builder with OpenAI embeddings.
        """

        print("Initializing OpenAI Embeddings...")

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_API_KEY"]
        )

        print("OpenAI embeddings initialized successfully.")


    def build_hybrid_retriever(self, docs):
        """
        Build a hybrid retriever using BM25 keyword search
        and Chroma vector similarity search.
        """

        try:

            # Create Chroma vector database
            vector_store = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_DB_PATH,
                collection_name=settings.CHROMA_COLLECTION_NAME
            )

            logger.info("Chroma vector store created successfully.")


            # Create BM25 keyword retriever
            bm25 = BM25Retriever.from_documents(docs)

            logger.info("BM25 retriever created successfully.")


            # Create semantic vector retriever
            vector_retriever = vector_store.as_retriever(
                search_kwargs={
                    "k": settings.VECTOR_SEARCH_K
                }
            )

            logger.info("Vector retriever created successfully.")


            # Combine BM25 + Vector Search
            hybrid_retriever = EnsembleRetriever(
                retrievers=[
                    bm25,
                    vector_retriever
                ],
                weights=settings.HYBRID_RETRIEVER_WEIGHTS
            )


            logger.info("Hybrid retriever created successfully.")

            return hybrid_retriever


        except Exception as e:
            logger.error(
                f"Failed to build hybrid retriever: {e}"
            )
            raise