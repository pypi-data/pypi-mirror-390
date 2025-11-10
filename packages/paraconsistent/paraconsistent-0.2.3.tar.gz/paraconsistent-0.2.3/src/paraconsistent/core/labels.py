from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ThresholdsAsym:
    ftc_pos: float; ftc_neg: float
    fd_pos: float;  fd_neg: float
    eps: float = 1e-12

def classify_12_regions_asymmetric(Dc: float, Dct: float, th: ThresholdsAsym) -> str:
    eps = th.eps

    # 0) centro exato
    if abs(Dc) <= eps and abs(Dct) <= eps:
        return "I"

    # 1) certeza dominante (assimétrica)
    if Dc >= th.ftc_pos:  # t
        return "t"
    if Dc <= -th.ftc_neg: # f
        return "f"

    # 2) contradição dominante (assimétrica)
    if Dct >= th.fd_pos:   # ┬
        return "┬"
    if Dct <= -th.fd_neg:  # ┴
        return "┴"

    # 3) quadrado central
    in_central = (Dc < th.ftc_pos and Dc > -th.ftc_neg and Dct < th.fd_pos and Dct > -th.fd_neg)
    if in_central:
        a, b = abs(Dc), abs(Dct)
        if b > a:
            # contradição/indeterminação domina - verificar sinal de Dct
            if Dct >= 0:
                # tendência à inconsistência (┬)
                return "Q┬→t" if Dc >= 0 else "Q┬→f"
            else:
                # tendência à indeterminação (┴)
                return "Q┴→t" if Dc >= 0 else "Q┴→f"
        elif a > b:
            # certeza domina
            if Dc >= 0:
                return "Qt→┬" if Dct >= 0 else "Qt→┴"
            else:
                return "Qf→┬" if Dct >= 0 else "Qf→┴"
        else:
            # empate: preferir Qt/Qf e setar seta pelo sinal de DCT
            if Dc >= 0:
                return "Qt→┬" if Dct >= 0 else "Qt→┴"
            else:
                return "Qf→┬" if Dct >= 0 else "Qf→┴"

    # fallback
    return "I"


def regions_flags(label: str) -> dict:
    # booleans por região para paridade com estruturas antigas
    keys = ["t","f","┬","┴","Q┬→t","Q┬→f","Qt→┬","Qf→┬","Qt→┴","Qf→┴","Q┴→t","Q┴→f","I"]
    return {k: (k == label) for k in keys}