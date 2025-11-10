from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ThresholdsAsym:
    ftc_pos: float; ftc_neg: float
    fd_pos: float;  fd_neg: float
    eps: float = 1e-12

def classify_12_regions_asymmetric(dc: float, dct: float, th: ThresholdsAsym) -> str:
    eps = th.eps

    # 0) centro exato
    if abs(dc) <= eps and abs(dct) <= eps:
        return "I"

    # 1) certeza dominante (assimétrica)
    if dc >= th.ftc_pos:  # t
        return "t"
    if dc <= -th.ftc_neg: # f
        return "f"

    # 2) contradição dominante (assimétrica)
    if dct >= th.fd_pos:   # ┬
        return "┬"
    if dct <= -th.fd_neg:  # ┴
        return "┴"

    # 3) quadrado central
    in_central = (dc < th.ftc_pos and dc > -th.ftc_neg and dct < th.fd_pos and dct > -th.fd_neg)
    if in_central:
        a, b = abs(dc), abs(dct)
        if b > a:
            # contradição/indeterminação domina - verificar sinal de dct
            if dct >= 0:
                # tendência à inconsistência (┬)
                return "Q┬→t" if dc >= 0 else "Q┬→f"
            else:
                # tendência à indeterminação (┴)
                return "Q┴→t" if dc >= 0 else "Q┴→f"
        elif a > b:
            # certeza domina
            if dc >= 0:
                return "Qt→┬" if dct >= 0 else "Qt→┴"
            else:
                return "Qf→┬" if dct >= 0 else "Qf→┴"
        else:
            # empate: preferir Qt/Qf e setar seta pelo sinal de dct
            if dc >= 0:
                return "Qt→┬" if dct >= 0 else "Qt→┴"
            else:
                return "Qf→┬" if dct >= 0 else "Qf→┴"

    # fallback
    return "I"


def regions_flags(label: str) -> dict:
    # booleans por região para paridade com estruturas antigas
    keys = ["t","f","┬","┴","Q┬→t","Q┬→f","Qt→┬","Qf→┬","Qt→┴","Qf→┴","Q┴→t","Q┴→f","I"]
    return {k: (k == label) for k in keys}