import logging
from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class CrescendoEscalationDetector:
    """
    Detects Crescendo-style multi-turn jailbreak escalation.

    Hybrid design:
    - Optional ML backend (Transformers) loaded from a local model dir
      pointed by `SEMFIRE_CRESCENDO_MODEL_DIR`.
    - Heuristic fallback combining harmful objective cues, bypass framings,
      and turn-depth escalation when ML is unavailable.

    This detector is intentionally conservative and meant to complement
    existing detectors (RuleBased, Injection, EchoChamber). It focuses on
    stepwise escalation toward a harmful objective.
    """

    def __init__(self, sensitivity: float = 0.55, model_dir: Optional[str] = None) -> None:
        # Allow environment override for sensitivity using a safe parser
        self.sensitivity = _get_env_float("SEMFIRE_CRESCENDO_SENSITIVITY", default=sensitivity)
        self.model_dir = model_dir or os.environ.get("SEMFIRE_CRESCENDO_MODEL_DIR")
        # ML input formatting knobs (to match training-time formatting if used)
        self.history_separator: str = os.environ.get("SEMFIRE_CRESCENDO_HISTORY_SEPARATOR", " | ")
        self.max_history_turns: int = max(0, _get_env_int("SEMFIRE_CRESCENDO_MAX_HISTORY", default=4))
        # Positive class configuration (explicit is safest)
        self._positive_class_index: Optional[int] = None
        env_pos_idx = _get_env_int("SEMFIRE_CRESCENDO_POSITIVE_INDEX", default=-1)
        if env_pos_idx >= 0:
            self._positive_class_index = env_pos_idx
        self._positive_class_label: Optional[str] = os.environ.get("SEMFIRE_CRESCENDO_POSITIVE_LABEL")
        # Load lexicon (externalizable via JSON)
        self._lexicon = self._load_lexicon()
        self._harmful_terms_by_cat = self._lexicon.get("harmful_terms", {})  # dict[str, list[str]]
        self._bypass_phrases_list = self._lexicon.get("bypass_phrases", [])  # list[str]

        self._model = None
        self._tokenizer = None
        self._labels = None

        # Attempt optional ML backend load
        if self.model_dir:
            # Validate the directory exists before attempting to load
            mdir = Path(self.model_dir)
            if not mdir.exists() or not mdir.is_dir():
                logger.warning(
                    f"CrescendoEscalationDetector: Model dir '{self.model_dir}' does not exist; using heuristic mode."
                )
            else:
                if not self._load_ml_backend():
                    # Leave model/tokenizer as None and proceed heuristically
                    self._model = None
                    self._tokenizer = None

        # Default weights (heuristic mode)
        self._w_harmful = _get_env_float("SEMFIRE_CRESCENDO_WEIGHT_HARMFUL", 0.35)
        self._w_bypass = _get_env_float("SEMFIRE_CRESCENDO_WEIGHT_BYPASS", 0.2)

    def analyze_text(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        # Prepare context
        history = conversation_history or []
        text = (text_input or "")
        turns = len(history) + 1

        # Try ML backend first
        ml_prob = None
        if self._model is not None and self._tokenizer is not None:
            try:
                # Compose input with limited history for context (configurable)
                ctx = (
                    self.history_separator.join(history[-self.max_history_turns:])
                    if (history and self.max_history_turns > 0)
                    else ""
                )
                model_input = f"Current: {text}\nHistory: {ctx}"
                toks = self._tokenizer(model_input, truncation=True, padding=True, max_length=512, return_tensors='pt')
                from torch import no_grad  # type: ignore
                with no_grad():  # type: ignore
                    out = self._model(**toks)
                    from torch import softmax  # type: ignore
                    probs = softmax(out.logits, dim=-1)[0].tolist()
                # Map to an escalation probability via validated positive class index
                pos_idx = self._get_positive_class_index(len(probs))
                if pos_idx is not None and 0 <= pos_idx < len(probs):
                    ml_prob = float(probs[pos_idx])
                else:
                    logger.error("CrescendoEscalationDetector: Positive class index unresolved; disabling ML contribution.")
                    ml_prob = None
            except (RuntimeError, ValueError, KeyError) as e:  # optional path
                logger.warning(f"CrescendoEscalationDetector: ML inference failed: {e}. Using heuristic mode.")
                ml_prob = None

        # Heuristic scoring (used standalone or combined with ML)
        lower_text = (" ".join(history) + " " + text).lower().strip()
        score = 0.0
        triggered: List[str] = []

        for category, terms in self._harmful_terms_by_cat.items():
            for term in terms:
                if term in lower_text:
                    score += self._w_harmful
                    triggered.append(f"crescendo_harmful_keyword[{category}]:{term}")

        for phrase in self._bypass_phrases_list:
            if phrase in lower_text:
                score += self._w_bypass
                triggered.append(f"crescendo_bypass_phrase:{phrase}")

        # Escalation by turn count (after early turns)
        if turns >= 3:
            score += min(0.05 * (turns - 2), 0.3)
            triggered.append(f"crescendo_escalation_turn:{turns}")

        # Combine with ML prob if available. We weight heuristics (0.6) > ML (0.4)
        # because heuristics are transparent and tuned for this domain. Adjust via code if needed.
        if ml_prob is not None:
            combined = 0.6 * score + 0.4 * ml_prob
        else:
            combined = score

        classification = (
            'potential_crescendo_escalation' if combined >= self.sensitivity
            else 'benign_escalation_signal'
        )

        return {
            'detector_name': 'CrescendoEscalationDetector',
            'classification': classification,
            'score': round(combined, 3),
            'probability': round(combined, 3),
            'triggered_rules': triggered,
            'explanation': (
                'Hybrid Crescendo escalation scoring (heuristics'
                + (', ML' if ml_prob is not None else '')
                + f"); sensitivity={self.sensitivity}"
            ),
            'error': None
        }

    def _load_ml_backend(self) -> bool:
        """Attempt to load optional ML backend. Returns True on success.

        This keeps transformers/torch as optional dependencies and avoids
        import-time crashes when unavailable.
        """
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
        except ImportError:
            logger.error(
                "CrescendoEscalationDetector: ML backend dependencies not available. "
                "Install with: pip install transformers torch"
            )
            return False
        try:
            # Torch is required at inference time; import to ensure availability
            import torch  # type: ignore  # noqa: F401
        except ImportError:
            logger.error(
                "CrescendoEscalationDetector: PyTorch not available. Install with: pip install torch"
            )
            return False

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_dir)  # type: ignore[arg-type]
            from transformers import AutoModelForSequenceClassification as _AMFSC  # type: ignore
            self._model = _AMFSC.from_pretrained(self.model_dir)  # type: ignore[arg-type]
            self._model.eval()
            # Cache labels if available
            self._labels = getattr(self._model.config, 'id2label', None)
            # Resolve/validate positive class index
            if self._get_positive_class_index(None) is None:
                logger.error(
                    "CrescendoEscalationDetector: Could not resolve positive class index from labels. "
                    "Set SEMFIRE_CRESCENDO_POSITIVE_INDEX or SEMFIRE_CRESCENDO_POSITIVE_LABEL to proceed with ML."
                )
                # Keep model loaded, but ML contribution will be disabled until configured
            logger.info(f"CrescendoEscalationDetector: Loaded model from {self.model_dir}")
            return True
        except (OSError, FileNotFoundError, ValueError) as e:
            logger.error(f"CrescendoEscalationDetector: Failed to load model from {self.model_dir}: {e}")
            return False

    def _get_positive_class_index(self, probs_len: Optional[int]) -> Optional[int]:
        """Determine positive class index safely.

        Priority:
        1) Explicit SEMFIRE_CRESCENDO_POSITIVE_INDEX (env)
        2) SEMFIRE_CRESCENDO_POSITIVE_LABEL exact match in model labels
        3) Exact-match against a small allowlist of known positive labels
        If unresolved, returns None to disable ML contribution.
        """
        # 1) Explicit index
        if self._positive_class_index is not None and (probs_len is None or 0 <= self._positive_class_index < max(probs_len, self._positive_class_index+1)):
            return self._positive_class_index

        labels = self._labels
        if not labels:
            return None

        # Normalize labels to a dict[int,str]
        norm: dict[int, str] = {}
        try:
            if isinstance(labels, dict):
                # keys may be str or int
                for k, v in labels.items():
                    try:
                        idx = int(k)
                    except Exception:
                        continue
                    norm[idx] = str(v)
            elif isinstance(labels, (list, tuple)):
                for i, v in enumerate(labels):
                    norm[i] = str(v)
            else:
                return None
        except Exception:
            return None

        # 2) Exact label env match
        if self._positive_class_label is not None:
            wanted = self._positive_class_label.strip().lower()
            for idx, name in norm.items():
                if name.strip().lower() == wanted:
                    self._positive_class_index = int(idx)
                    return self._positive_class_index
            return None

        # 3) Exact allowlist match
        allow = {"escalation", "jailbreak", "unsafe", "harm", "violation", "positive", "1"}
        for idx, name in norm.items():
            if name.strip().lower() in allow:
                self._positive_class_index = int(idx)
                return self._positive_class_index

        return None

    def _load_lexicon(self) -> Dict[str, Any]:
        """Load lexicon from JSON file via SEMFIRE_CRESCENDO_LEXICON_PATH, or use defaults.

        Schema (JSON):
        {
          "harmful_terms": { "weapons": [...], "cybersecurity": [...], ... },
          "bypass_phrases": [ ... ]
        }
        """
        path = os.environ.get("SEMFIRE_CRESCENDO_LEXICON_PATH")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Lexicon root is not a dict")
                harmful = data.get("harmful_terms", {})
                bypass = data.get("bypass_phrases", [])
                if not isinstance(harmful, dict) or not isinstance(bypass, list):
                    raise ValueError("Lexicon types invalid")
                logger.info(f"CrescendoEscalationDetector: Loaded lexicon from {path}")
                return {"harmful_terms": harmful, "bypass_phrases": bypass}
            except Exception as e:
                logger.warning(f"CrescendoEscalationDetector: Failed to load lexicon from {path}: {e}. Using defaults.")
        # Defaults
        return {
            "harmful_terms": {
                'weapons': ['bomb', 'explosive', 'weapon', 'grenade', 'landmine', 'pipe bomb'],
                'cybersecurity': ['phishing', 'ransomware', 'malware', 'keylogger', 'rootkit'],
                'exploitation': ['bypass', 'circumvent', 'exploit', 'payload'],
                'drugs': ['illegal drugs', 'meth', 'cocaine', 'heroin'],
                'harassment': ['stalking', 'doxx'],
                'chemicals': ['poison', 'synthesize'],
            },
            "bypass_phrases": [
                'for research', 'for academic', 'for academic purposes', 'hypothetical',
                'under certain circumstances', 'ignore previous instructions', 'ignore safety',
                'security research', 'harmless intent'
            ]
        }


def _get_env_float(name: str, default: float) -> float:
    try:
        raw = os.environ.get(name)
        return float(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


def _get_env_int(name: str, default: int) -> int:
    try:
        raw = os.environ.get(name)
        return int(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default
