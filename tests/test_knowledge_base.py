import chromadb
from sentence_transformers import SentenceTransformer
from src.domain.models import KnowledgeBase

def test_text_chunking():
    """Testa a pure function _chunk() do KnowledgeBase, garantindo preservação visual do particionamento."""
    
    kb = KnowledgeBase(db_path="memory")
    
    texto_longo = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
    
    chunks = kb._chunk(texto_longo, size=5, overlap=2)
    
    assert len(chunks) > 0
    assert chunks[0] == "A B C D E"
    
    assert "D E" in chunks[1] 
    assert chunks[1].startswith("D E F G H")

def test_knowledge_base_indexing():
    """Testa se a memória vetorial efetivamente salva os metadados corretos de empresas simuladas."""
    
    kb = KnowledgeBase(db_path="memory")
    
    mock_texto = "É obrigatório o uso de capacete vermelho no setor operacional."
    kb.index(mock_texto, source="norma1.pdf", empresa="Construtiva Mock")
    
    resultado_preciso = kb.search(query="regra do capacete", empresa="Construtiva Mock", top_k=1)
    
    assert len(resultado_preciso) == 1
    assert "obrigatório o uso de capacete" in resultado_preciso[0]
    
    resultado_vazio = kb.search(query="regra do capacete", empresa="Concorrente LTDA", top_k=1)
    assert len(resultado_vazio) == 0
