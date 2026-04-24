from pathlib import Path
from ultralytics import YOLO
from loguru import logger
import cv2
from src.models import PersonResponse
from src.interfaces import BaseDetector


class PersonDetector(BaseDetector):
    def __init__(self, location: Path, threshold: float = 0.5) -> None:
        """Inicializa o detector de pessoas"""

        if not location.exists():
            raise FileNotFoundError(f"modelo não encontrado: {location}")

        self._detector: YOLO = YOLO(str(location))
        self._threshold: float = threshold

    def detect(self, path: Path) -> list[PersonResponse]:
        """Detecta pessoas na imagem e retorna lista de PersonResponse."""

        if not path.exists():
            raise FileNotFoundError(f"imagem não encontrada: {path}")

        # classes=[0] filtra só pessoa no dataset coco
        results = self._detector(str(path), classes=[0], conf=self._threshold)

        image: cv2.Mat = results[0].orig_img
        boxes = results[0].boxes

        persons: list[PersonResponse] = []
        for i, (box, conf) in enumerate(zip(boxes.xyxy, boxes.conf)):
            x1, y1, x2, y2 = map(int, box)
            crop: cv2.Mat = image[y1:y2, x1:x2]

            persons.append(PersonResponse(
                id=i+1,
                confidence=float(conf),
                box={'x_min': x1, 'y_min': y1, 'x_max': x2, 'y_max': y2},
                crop=crop
            ))

        logger.info(f"pessoas encontradas: {len(persons)}")
        return persons

    def draw_boxes(self, image: cv2.Mat, persons: list[PersonResponse]) -> cv2.Mat:
        """Desenha caixas nas pessoas"""

        for person in persons:
            x1, y1, x2, y2 = person.box["x_min"], person.box["y_min"], person.box["x_max"], person.box["y_max"]
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{person.id} {person.confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return image

    def crop_and_save(self, persons: list[PersonResponse], output_dir: Path) -> None:
        """Salva as pessoas detectadas em arquivos separados."""
        output_dir.mkdir(parents=True, exist_ok=True)

        for person in persons:
            cv2.imwrite(str(output_dir / f"{person.id}.png"), person.crop)
            logger.debug(f"{person.id} salvo em {output_dir}")
    