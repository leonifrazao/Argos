from pathlib import Path
from sentence_transformers import SentenceTransformer
from loguru import logger
import chromadb
from itertools import chain

from src.models import ComplianceContext
from src.interfaces import BaseKnowledgeBase, BaseParser


class KnowledgeBase(BaseKnowledgeBase):
    def __init__(self, model: str = "all-MiniLM-L6-v2", db_path: str = "chroma_db") -> None:
        """Inicializa a base de conhecimento com vector store local."""
        self._client: chromadb.PersistentClient = chromadb.PersistentClient(path=db_path)
        self._collection: chromadb.Collection = self._client.get_or_create_collection("manuals")
        self._embedder: SentenceTransformer = SentenceTransformer(model)

    def index(self, text: str, source: str, empresa: str) -> None:
        """Indexa chunks de um documento."""
        chunks: list[str] = self._chunk(text)

        for i, chunk in enumerate(chunks):
            embedding: list[float] = self._embedder.encode(chunk).tolist()
            self._collection.upsert(
                ids=[f"{empresa}_{source}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": source, "empresa": empresa}]
            )

        logger.info(f"indexado: {source} | empresa: {empresa} ({len(chunks)} chunks)")

    def search(self, query: str, empresa: str = "", top_k: int = 5) -> list[str]:
        """Busca chunks relevantes por similaridade semântica filtrando opcionalmente por empresa."""
        embedding: list[float] = self._embedder.encode(query).tolist()

        query_args = {
            "query_embeddings": [embedding],
            "n_results": top_k
        }

        if empresa != "":
            query_args["where"] = {"empresa": empresa}

        results: dict[str, list[list[str]]] = self._collection.query(**query_args)

        chunks: list[str] = results.get("documents", [[]])[0]

        if not chunks:
            logger.warning(f"nenhum chunk encontrado para query: '{query}' | empresa: {empresa}")

        return chunks

    def index_dataset(self, dataset_path: Path, parser: BaseParser) -> None:
        """Indexa todos os PDFs e DOCXs separados por empresa."""

        files: list[Path] = list(chain(
            dataset_path.rglob("*.pdf"),
            dataset_path.rglob("*.docx")
        ))

        if not files:
            raise FileNotFoundError(f"nenhum arquivo encontrado em: {dataset_path}")

        for file in files:
            empresa = file.relative_to(dataset_path).parts[0]
            
            text = parser.parse(file)
            self.index(text, source=file.name, empresa=empresa)

            logger.info(f"indexado: {file.name} | empresa: {empresa}")

        logger.info(f"dataset indexado: {len(files)} arquivos")

    def _chunk(self, text: str, size: int = 500, overlap: int = 50) -> list[str]:
        """Divide texto em chunks com overlap para não perder contexto entre chunks."""
        words: tuple[str, ...] = tuple(text.split())
        chunks: list[str] = []

        for i in range(0, len(words), size - overlap):
            chunk = " ".join(words[i:i + size])
            if chunk:
                chunks.append(chunk)

        return chunks