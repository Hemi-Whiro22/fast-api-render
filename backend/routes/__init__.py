# -*- coding: utf-8 -*-
"""Route modules exported for FastAPI inclusion."""

from . import embed, memory, translate
# OCR route disabled: requires tesseract and PIL (complex deployment)

__all__ = [
    "embed",
    "memory",
    "translate",

]
