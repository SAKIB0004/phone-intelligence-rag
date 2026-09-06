from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions


def create_embedding_function(model_name: str) -> EmbeddingFunction:
	"""Create the shared Sentence Transformer function used by ChromaDB."""
	return embedding_functions.SentenceTransformerEmbeddingFunction(
		model_name=model_name
	)
