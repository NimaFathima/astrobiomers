"""
Named Entity Recognition (NER) utilities for the Space Biology Knowledge Graph.

This module keeps heavyweight transformer and spaCy integrations optional so
local smoke tests can run without downloading large model artifacts. Pattern
matching remains available in all environments.
"""

from __future__ import annotations

from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

# Optional dependencies -----------------------------------------------------
try:  # pragma: no cover - large optional dependency
    from transformers import pipeline as hf_pipeline  # type: ignore
except Exception:  # pragma: no cover
    hf_pipeline = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore


class EntityExtractor:
    """Primary entity extraction engine with optional ML backends."""

    def __init__(
        self,
        scibert_model: str = "allenai/scibert_scivocab_uncased",
        use_gpu: bool = True,
        confidence_threshold: float = 0.75,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.confidence_threshold = confidence_threshold

        if torch is not None and use_gpu and torch.cuda.is_available():  # pragma: no cover
            self.device = 0
            self.logger.info("Using GPU for transformer-based NER")
        else:
            self.device = -1
            self.logger.info("Using CPU / pattern-based NER")

        self.scibert_ner = None
        if hf_pipeline is not None and torch is not None:
            try:  # pragma: no cover - heavy download path
                self.logger.info("Loading SciBERT model: %s", scibert_model)
                self.scibert_ner = hf_pipeline(
                    "ner",
                    model=scibert_model,
                    tokenizer=scibert_model,
                    aggregation_strategy="simple",
                    device=self.device,
                )
                self.logger.info("SciBERT model loaded successfully")
            except Exception as exc:  # pragma: no cover
                self.logger.warning("SciBERT unavailable, continuing without transformers: %s", exc)
                self.scibert_ner = None
        else:
            self.logger.info("Transformers/torch not installed; skipping SciBERT model.")

        self.scispacy_nlp = None
        if spacy is not None:
            try:  # pragma: no cover - requires external download
                self.logger.info("Loading SciSpaCy model: en_ner_bc5cdr_md")
                self.scispacy_nlp = spacy.load("en_ner_bc5cdr_md")
                self.logger.info("SciSpaCy model loaded successfully")
            except Exception as exc:  # pragma: no cover
                self.logger.warning("SciSpaCy model unavailable, continuing without it: %s", exc)
                self.scispacy_nlp = None
        else:
            self.logger.info("spaCy not installed; relying on pattern-based extraction.")

        self.entity_type_map = {
            "GENE": "GENE",
            "PROTEIN": "GENE",
            "DISEASE": "DISEASE",
            "CHEMICAL": "METABOLITE",
            "CELL_LINE": "CELL_LINE",
            "CELL_TYPE": "CELL_TYPE",
            "SPECIES": "ORGANISM",
        }

    def extract_entities(self, text: str) -> List[Dict]:
        if not text or not text.strip():
            return []

        entities: List[Dict] = []

        if self.scibert_ner is not None:
            entities.extend(self._extract_with_scibert(text))

        if self.scispacy_nlp is not None:
            entities.extend(self._extract_with_scispacy(text))

        entities.extend(self._extract_space_biology_entities(text))

        entities = self._deduplicate_entities(entities)
        return [e for e in entities if e["confidence"] >= self.confidence_threshold]

    def extract_from_paper(self, paper: Dict) -> Dict:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        entities = self.extract_entities(text)

        paper["entities"] = entities
        paper["entity_count"] = len(entities)
        paper["entity_types"] = {}
        for entity in entities:
            etype = entity.get("type", "UNKNOWN")
            paper["entity_types"][etype] = paper["entity_types"].get(etype, 0) + 1
        return paper

    def extract_from_papers_batch(self, papers: List[Dict]) -> List[Dict]:
        self.logger.info("Extracting entities from %d papers", len(papers))
        for paper in papers:
            try:
                self.extract_from_paper(paper)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.error("Entity extraction failed for paper %s: %s", paper.get("pmid"), exc)
                paper.setdefault("entities", [])
                paper.setdefault("entity_types", {})
                paper.setdefault("entity_count", 0)
        return papers

    def _extract_pattern_based_entities(self, text: str) -> Dict[str, List[str]]:
        grouped: Dict[str, List[str]] = {}
        for entity in self._extract_space_biology_entities(text):
            grouped.setdefault(entity["type"], []).append(entity["text"])
        return grouped

    def _extract_with_scibert(self, text: str) -> List[Dict]:
        if self.scibert_ner is None:
            return []

        try:  # pragma: no cover - relies on heavy models
            results = self.scibert_ner(text)
        except Exception as exc:  # pragma: no cover
            self.logger.error("SciBERT extraction error: %s", exc)
            return []

        entities: List[Dict] = []
        for entity in results:
            entities.append(
                {
                    "type": self.entity_type_map.get(entity.get("entity_group"), entity.get("entity_group")),
                    "text": entity.get("word", "").strip(),
                    "start": entity.get("start"),
                    "end": entity.get("end"),
                    "confidence": entity.get("score", 0.0),
                    "source": "SciBERT",
                }
            )
        return entities

    def _extract_with_scispacy(self, text: str) -> List[Dict]:
        if self.scispacy_nlp is None:
            return []

        try:  # pragma: no cover - relies on heavy models
            doc = self.scispacy_nlp(text)
        except Exception as exc:  # pragma: no cover
            self.logger.error("SciSpaCy extraction error: %s", exc)
            return []

        entities: List[Dict] = []
        for ent in getattr(doc, "ents", []):
            entities.append(
                {
                    "type": self.entity_type_map.get(ent.label_, ent.label_),
                    "text": ent.text.strip(),
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.85,
                    "source": "SciSpaCy",
                }
            )
        return entities

    def _extract_space_biology_entities(self, text: str) -> List[Dict]:
        entities: List[Dict] = []

        stressor_patterns = {
            "Microgravity": r"\b(?:microgravity|micro-gravity|μg|ug|weightlessness|zero-?g)\b",
            "Simulated Microgravity": r"\b(?:simulated microgravity|clinostat|RPM|rotating wall vessel|hindlimb unloading|tail suspension)\b",
            "Cosmic Radiation": r"\b(?:cosmic radiation|GCR|galactic cosmic ray|space radiation|ionizing radiation)\b",
            "Solar Particle Event": r"\b(?:SPE|solar particle event|solar energetic particle|SEP)\b",
            "Hypergravity": r"\b(?:hypergravity|hyper-gravity|centrifuge|[2-9]g|[2-9] g)\b",
            "Isolation": r"\b(?:isolation|confinement|confined environment|psychological stress)\b",
            "Altered Gravity": r"\b(?:altered gravity|variable gravity|partial gravity|lunar gravity|martian gravity)\b",
            "Spaceflight": r"\b(?:spaceflight|space flight|space mission|ISS mission)\b",
        }

        phenotype_patterns = {
            "Bone Loss": r"\b(?:bone loss|bone density loss|osteopenia|osteoporosis|skeletal unloading)\b",
            "Muscle Atrophy": r"\b(?:muscle atrophy|muscle wasting|sarcopenia|muscle loss|skeletal muscle deconditioning)\b",
            "Immune Dysfunction": r"\b(?:immune dysfunction|immunosuppression|immune impairment|immune dysregulation)\b",
            "Fluid Shift": r"\b(?:fluid shift|cephalad fluid shift|facial edema|intracranial pressure)\b",
            "Vision Changes": r"\b(?:vision changes|visual impairment|spaceflight associated neuro-ocular syndrome|SANS|optic disc edema)\b",
            "Cardiovascular Changes": r"\b(?:cardiovascular deconditioning|orthostatic intolerance|cardiac atrophy)\b",
            "Sensorimotor Changes": r"\b(?:sensorimotor changes|spatial orientation|neurovestibular)\b",
        }

        for canonical, pattern in stressor_patterns.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                entities.append(
                    {
                        "type": "STRESSOR",
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.90,
                        "source": "Pattern",
                        "canonical_name": canonical,
                    }
                )

        for canonical, pattern in phenotype_patterns.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                entities.append(
                    {
                        "type": "PHENOTYPE",
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.88,
                        "source": "Pattern",
                        "canonical_name": canonical,
                    }
                )

        return entities

    @staticmethod
    def _deduplicate_entities(entities: List[Dict]) -> List[Dict]:
        if not entities:
            return []

        entities = sorted(entities, key=lambda e: (e.get("start", 0), -e.get("confidence", 0)))
        deduplicated: List[Dict] = []
        last_end = -1

        for entity in entities:
            start = entity.get("start", 0)
            end = entity.get("end", 0)
            if start >= last_end:
                deduplicated.append(entity)
                last_end = end
            elif deduplicated and entity.get("confidence", 0) > deduplicated[-1].get("confidence", 0):
                deduplicated[-1] = entity
                last_end = end
        return deduplicated


class NERExtractor(EntityExtractor):
    """Backward compatible alias kept for legacy imports."""


__all__ = ["EntityExtractor", "NERExtractor"]
