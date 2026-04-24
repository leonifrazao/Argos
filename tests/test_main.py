from unittest.mock import Mock, call
from pathlib import Path
from src.interfaces import BaseDetector, BaseParser, BaseKnowledgeBase, BaseAnalyzer, BaseSaver
from src.models import AppConfig, ComplianceResponse, PersonResponse
from main import Main


def test_main_orchestration_com_injecao_de_dependencia():
    """
    Testa se o orquestrador `Main` delega o fluxo corretamente para todas as interfaces
    (Parser, Detector, KnowledgeBase, Analyzer, Saver), sem depender de implementações pesadas 
    como ChromaDB, OpenCV ou chamadas de rede da Google Gemini.
    """
    
    mock_detector = Mock(spec=BaseDetector)
    mock_parser = Mock(spec=BaseParser)
    mock_kb = Mock(spec=BaseKnowledgeBase)
    mock_analyzer = Mock(spec=BaseAnalyzer)
    fake_person = PersonResponse(id=1, box={'x_min': 0, 'y_min': 0, 'x_max': 100, 'y_max': 100}, crop=b"fake_bytes", confidence=0.99)
    fake_rule = "Regra de teste para EPIs Mock."
    fake_compliance = ComplianceResponse(
        pessoa_id=1,
        status="Conforme",
        justificativa="OK",
        bbox=fake_person.box
    )
    
    mock_detector.detect.return_value = [fake_person]
    mock_kb.search.return_value = [fake_rule]
    mock_analyzer.analyze.return_value = [fake_compliance]
    
    mock_config = Mock()
    mock_config.chroma = Mock()
    mock_config.chroma.top_k = 5
    mock_config.output = Mock()
    mock_config.output.results_path = "output/test_results.json"
    
    main_app = Main(
        person_detector=mock_detector,
        file_parser=mock_parser,
        knowledge_base=mock_kb,
        analyzer=mock_analyzer,
        saver=mock_saver,
        config=mock_config
    )
    
    test_image_path = Path("dataset/Concorrente/images/img_test.jpg")
    main_app.run(
        image_path=test_image_path,
        empresa="Concorrente",
        setor="logistica_mock"
    )
    
    mock_detector.detect.assert_called_once_with(test_image_path)
    
    mock_kb.search.assert_called_once_with(
        query="regras de conformidade, vestimenta e equipamentos de segurança (epi). setor: logistica_mock",
        empresa="Concorrente",
        top_k=5
    )
    
    mock_analyzer.analyze.assert_called_once_with("gemini", [fake_person], [fake_rule])
    
    mock_saver.save.assert_called_once()
    args, _ = mock_saver.save.call_args
    assert args[0] == [fake_compliance]
    assert "output_concorrente_img_test.json" in str(args[1])
