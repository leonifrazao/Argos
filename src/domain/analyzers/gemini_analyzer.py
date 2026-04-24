from google import genai
from google.genai import types
from loguru import logger
import os
import cv2
from dotenv import load_dotenv

from src.interfaces import BaseAnalyzer
from src.models import PersonResponse, ComplianceResponse

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ServerError, ClientError


class GeminiAnalyzer(BaseAnalyzer):
    def __init__(self, model: str = "gemini-3-flash-preview", api_key: str | None = None) -> None:
        load_dotenv()
        self._client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
        self._model = model
        self._config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            response_mime_type="application/json",
            response_schema=genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["pessoa_id", "status", "justificativa"],
                    properties={
                        "pessoa_id": genai.types.Schema(type=genai.types.Type.INTEGER),
                        "status": genai.types.Schema(type=genai.types.Type.STRING),
                        "justificativa": genai.types.Schema(type=genai.types.Type.STRING),
                    },
                ),
            ),
            system_instruction=[
                types.Part.from_text(text="""
Você é um sistema de análise de conformidade visual.
Abaixo você receberá as regras de segurança/conformidade da empresa e uma série de fotos (recortes) de diferentes pessoas.
Para cada imagem com ID (apenas ID numérico) fornecido, verifique se a pessoa está em conformidade.
Responda sempre com status: "Conforme", "Não conforme" ou "Indeterminado".
A justificativa deve ser objetiva e baseada nas regras para aquele ID específico.
"""),
            ],
        )


    @retry(
        retry=retry_if_exception_type(ServerError | ClientError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        before_sleep=lambda state: logger.warning(f"gemini indisponível, tentativa {state.attempt_number}/3 — aguardando...")
    )
    def analyze(self, persons: list[PersonResponse], rules: list[str]) -> list[ComplianceResponse]:
        """Analisa conformidade de múltiplas pessoas em lote com base nas regras recuperadas."""

        if not persons:
            return []

        logger.info(f"analisando lote de {len(persons)} pessoas com o modelo {self._model}")

        if not rules:
            logger.warning("nenhuma regra encontrada para análise")
            return [
                ComplianceResponse(
                    pessoa_id=pessoa.id,
                    bbox=pessoa.box,
                    status="Indeterminado",
                    justificativa="Nenhuma regra encontrada para este contexto."
                ) for pessoa in pessoas
            ]

        parts = [types.Part.from_text(text="Refira-se às seguintes regras de conformidade:\n" + "\n".join(rules))]
        parts.append(types.Part.from_text(text="\nAvalie as imagens das seguintes pessoas:"))

        for person in persons:
            _, buffer = cv2.imencode(".jpg", person.crop)
            parts.append(types.Part.from_text(text=f"Pessoa ID: {person.id}"))
            parts.append(types.Part.from_bytes(data=buffer.tobytes(), mime_type="image/jpeg"))

        contents = [types.Content(role="user", parts=parts)]

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=self._config,
        )

        data = response.parsed
        results = []
        persons_map = {p.id: p for p in persons}

        # O modelo pode eventualmente não retornar para todas as pessoas
        ids_processados = set()

        for item in data:
            pid = item.get("pessoa_id")
            if pid in persons_map:
                status_cru = item.get("status", "Indeterminado").capitalize()
                status = "Não conforme" if status_cru == "Não conforme" or status_cru == "Nao conforme" else status_cru
                justificativa = item.get("justificativa", "")
                
                logger.info(f"{pid} → {status}")
                results.append(ComplianceResponse(
                    pessoa_id=pid,
                    bbox=persons_map[pid].box,
                    status=status,
                    justificativa=justificativa
                ))
                ids_processados.add(pid)

        # Adiciona resposta default pras pessoas que a IA não processou/esquecer
        for pid, person in persons_map.items():
            if pid not in ids_processados:
                logger.warning(f"modelo esqueceu de processar {pid}")
                results.append(ComplianceResponse(
                    pessoa_id=pid,
                    bbox=person.box,
                    status="Indeterminado",
                    justificativa="Modelo da Google falhou em processar dados suficientes."
                ))

        return results