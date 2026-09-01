"""indic_normalizer — a lightweight TTS pre-normalizer for the 22 scheduled
Indian languages (+ English).

Public API::

    from indic_normalizer import Normalizer, normalize
    normalize("भारत 1947 में स्वतंत्र हुआ", lang="hi")

See :class:`~indic_normalizer.config.NormalizerConfig` for options.
"""

from .config import NormalizerConfig, SUPPORTED_LANGS
from .normalizer import Normalizer, normalize

# LaTeX helper re-exported lazily to avoid import cost when unused.
try:
    from .latex import latex_to_speech
except Exception:  # pragma: no cover - engine may be built separately
    latex_to_speech = None

__version__ = "0.1.0"

__all__ = [
    "Normalizer",
    "normalize",
    "NormalizerConfig",
    "SUPPORTED_LANGS",
    "latex_to_speech",
    "__version__",
]
