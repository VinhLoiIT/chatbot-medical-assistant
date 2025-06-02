from agno.vectordb.weaviate import Weaviate
from agno.embedder.google import GeminiEmbedder
from agno.knowledge import AgentKnowledge
from configs.settings import settings
import weaviate

vector_db = Weaviate(
    client=weaviate.connect_to_custom(
        http_host=settings.WEAVIATE_HTTP_HOST,
        http_port=settings.WEAVIATE_HTTP_PORT,
        grpc_host=settings.WEAVIATE_GRPC_HOST,
        grpc_port=settings.WEAVIATE_GRPC_PORT,
        http_secure=False,
        grpc_secure=False,
        auth_credentials=weaviate.auth.AuthApiKey("user-a-key"),
    ),
    embedder=GeminiEmbedder(
        dimensions=1536,
        id="gemini-embedding-exp-03-07",
        task_type="RETRIEVAL_QUERY",
        api_key=settings.GEMINI_API_KEY,
    ),
    collection="default",
    # reranker=Reranker()  # TODO: to simplify, let's not use reranker for now
)
vector_db.create()

knowledge_base = AgentKnowledge(
    vector_db=vector_db,
    num_documents=settings.DEFAULT_DOC_RETRIEVAL_NUM,
)


def clear_knowledge_base():
    client = vector_db.get_client()
    client.connect()
    client.collections.delete(vector_db.collection)
    vector_db.create()


def get_kb_vector_db_collection():
    client = vector_db.get_client()
    client.connect()
    return client.collections.get(vector_db.collection)
