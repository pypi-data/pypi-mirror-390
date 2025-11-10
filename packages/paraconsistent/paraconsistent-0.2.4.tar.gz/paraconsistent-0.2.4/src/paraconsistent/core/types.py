from __future__ import annotations
from typing import Dict, TypedDict


__all__ = ["Complete"]


class Complete(TypedDict):
    # parâmetros (VSSC, VICC, VSSCT, VICCT são calculados automaticamente)
    FtC: float
    VlV: float; VlF: float; L: float
    # entradas
    mu: float; lam: float
    # graus e derivados
    dc: float; dct: float
    d: float; D: float; dcr: float
    # evidências
    muE: float; muECT: float; muER: float
    phi: float; phiE: float
    # decisão
    decision_output: float
    # classificação
    label: str
    Regions: dict[str, bool]