from abc import ABC, abstractmethod

class BaseKnowledgeBase(ABC):
    @abstractmethod
    def index(self, text: str, source: str, empresa: str) -> None: ...

    @abstractmethod
    def search(self, query: str, empresa: str = None, top_k: int = 5) -> list[str]: ...