from pathlib import Path
from src.domain.models import ResultSaver
from src.domain.savers import JsonSaver
from src.models import ComplianceResponse
import json
import pytest

def test_result_saver_registry():
    saver = ResultSaver()
    json_saver = JsonSaver()
    
    saver.register(".json", json_saver)
    assert ".json" in saver._savers
    assert saver._savers[".json"] == json_saver

def test_result_saver_unsupported_extension():
    saver = ResultSaver()
    
    with pytest.raises(ValueError, match="formato não suportado para salvamento"):
        saver.save([], Path("arquivo_fake.csv"))

def test_json_saver_writes_file(tmp_path: Path):
    saver = JsonSaver()
    mock_data = [
        ComplianceResponse(
            pessoa_id=1,
            status="Não conforme",
            justificativa="Sem capacete",
            bbox={'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}
        )
    ]
    
    file_path = tmp_path / "test_output.json"
    saver.save(mock_data, file_path)
    
    assert file_path.exists()
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) == 1
    assert data[0]["pessoa_id"] == 1
    assert data[0]["bbox"] == {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}
