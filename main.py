from src.domain.models import PersonDetector, KnowledgeBase, FileParser, AnalyzerRegistry, ResultSaver
from src.domain.analyzers import GeminiAnalyzer
from src.domain.savers import JsonSaver
from src.models import PersonResponse, ComplianceResponse, AppConfig
from pathlib import Path
from src.interfaces import BaseDetector, BaseParser, BaseKnowledgeBase, BaseAnalyzer, BaseSaver
from src.domain.parsers import PdfParser, DocxParser
from src.infrastructure import ConfigLoader
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import re


console = Console()

class Main:
    def __init__(
        self,
        person_detector: BaseDetector,
        file_parser: BaseParser,
        knowledge_base: BaseKnowledgeBase,
        analyzer: BaseAnalyzer,
        saver: BaseSaver,
        config: AppConfig,
    ) -> None:
        self.person_detector: BaseDetector = person_detector
        self.file_parser: BaseParser = file_parser
        self.knowledge_base: BaseKnowledgeBase = knowledge_base
        self.analyzer: BaseAnalyzer = analyzer
        self.saver: BaseSaver = saver
        self.config: AppConfig = config
    
    def _format_empresa(self, empresa: str) -> str:
        empresa_formatada = re.sub(r'[^a-zA-Z0-9]', '_', empresa).lower().strip('_')
        empresa_formatada = re.sub(r'_+', '_', empresa_formatada)
        return empresa_formatada
    
    def _gerar_caminho_arquivo(self, empresa: str, image_path: Path) -> Path:
        empresa_formatada = self._format_empresa(empresa)
        nome_arquivo = f"output_{empresa_formatada}_{image_path.stem}.json"
        base_dir = Path(self.config.output.results_path).parent
        base_dir.mkdir(parents=True, exist_ok=True)
        caminho_final = base_dir / nome_arquivo
        return caminho_final

    def run(self, image_path: Path, empresa: str, setor: str) -> None:
        persons: list[PersonResponse] = self.person_detector.detect(image_path)
        
        rules = self.knowledge_base.search(
            query=f"regras de conformidade, vestimenta e equipamentos de segurança (epi). setor: {setor}", 
            empresa=empresa,
            top_k=self.config.chroma.top_k
        )
        
        results = self.analyzer.analyze("gemini", persons, rules)

        self._display(results)
        
        caminho_final = self._gerar_caminho_arquivo(empresa, image_path)
        
        self.saver.save(results, caminho_final)

    def index_dataset(self) -> None:
        self.knowledge_base.index_dataset(Path(self.config.dataset.path), self.file_parser)

    def _display(self, results: list[ComplianceResponse]) -> None:
        console = Console()
        
        import json
        dicts_limpos = [res.model_dump() for res in results]
        console.print("\n[bold yellow]PARECER FORMATO ESTRITO (JSON)[/bold yellow]")
        console.print_json(json.dumps(dicts_limpos))

        table = Table(title="Análise de Conformidade (Dashboard)")

        table.add_column("id", style="cyan")
        table.add_column("status", style="bold")
        table.add_column("justificativa")

        for r in results:
            color = "green" if r.status == "Conforme" else "red" if r.status == "Não conforme" else "yellow"
            table.add_row(str(r.pessoa_id), f"[{color}]{r.status}[/{color}]", r.justificativa)

        console.print(table)


if __name__ == "__main__":
    config: AppConfig = ConfigLoader.load("config.yaml")

    file_parser: BaseParser = FileParser()
    file_parser.register(".pdf", PdfParser())
    file_parser.register(".docx", DocxParser())

    analyzer = AnalyzerRegistry()
    analyzer.register("gemini", GeminiAnalyzer(model=config.gemini.model, api_key=config.gemini.api_key))
    
    saver = ResultSaver()
    saver.register(".json", JsonSaver())

    main: Main = Main(
        person_detector=PersonDetector(Path(config.yolo.model_path), threshold=config.yolo.threshold),
        file_parser=file_parser,
        knowledge_base=KnowledgeBase(model=config.chroma.embedder_model, db_path=config.chroma.db_path),
        analyzer=analyzer,
        saver=saver,
        config=config,
    )

    main.index_dataset()
    
    valid_extensions = {".png", ".jpg", ".jpeg"}
    dataset_path = Path(config.dataset.path)
    image_files = [p for p in dataset_path.rglob("*") if p.suffix.lower() in valid_extensions]

    if not image_files:
        console.print("[bold red]Nenhuma imagem encontrada no dataset.[/bold red]")
        exit(1)

    console.print("\n[bold green]INICIANDO ANÁLISE EM LOTE[/bold green]")
    
    for img_path in image_files:
        try:
            empresa = img_path.relative_to(dataset_path).parts[0]
        except IndexError:
            continue

        console.print(f"\n[bold blue]>> Imagem Atual:[/bold blue] {img_path.name} | [bold cyan]Empresa:[/bold cyan] {empresa}")
        
        setor_selecionado = Prompt.ask("Qual categoria/setor de usuário gostaria de analisar para esta imagem?", default="operacional")

        main.run(
            image_path=img_path,
            empresa=empresa,
            setor=setor_selecionado
        )