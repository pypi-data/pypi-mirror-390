from __future__ import annotations
from types import SimpleNamespace
from typing import Dict, Tuple


from paraconsistent.core.metrics import clamp01, radial_d_to_nearest_apex
from paraconsistent.core.config import BlockParams
from paraconsistent.core.types import Complete
from paraconsistent.core.labels import ThresholdsAsym, classify_12_regions_asymmetric, regions_flags


__all__ = ["ParaconsistentEngine"]


class ParaconsistentEngine:

    @staticmethod
    def core_degrees(mu: float, lam: float) -> Tuple[float, float]:
        """Calcula graus de certeza e contradição.

        Args:
            mu: Grau de evidência favorável (0-1)
            lam: Grau de evidência desfavorável (0-1)

        Returns:
            Tupla (dc, dct) onde:
            - dc: degree of certainty
            - dct: degree of contradiction
        """
        dc = mu - lam
        dct = mu + lam - 1.0
        return dc, dct


    @staticmethod
    def geometry(mu: float, lam: float, dc: float) -> Tuple[float, float, float]:
        """Calcula métricas geométricas e certeza radial.

        Args:
            mu: Grau de evidência favorável
            lam: Grau de evidência desfavorável
            dc: degree of certainty

        Returns:
            Tupla (d, D, dcr) onde:
            - d: Distância radial
            - D: Distância normalizada (clampada em 1.0)
            - dcr: degree of real certainty
        """
        d = radial_d_to_nearest_apex(mu, lam)
        D = min(d, 1.0)  # Clampar D em 1.0 para alinhar com planilha de referência
        dcr = (1.0 - D) * (1.0 if dc >= 0 else -1.0)
        return d, D, dcr

    @staticmethod
    def classify(ftc: float, vlv: float, vlf: float, dc: float, dct: float) -> Tuple[str, dict]:
        """Classifica o estado lógico em uma das 12 regiões.

        Args:
            ftc: Certainty Control Limit (CCL)
            vlv: Viés pró-verdadeiro
            vlf: Viés pró-falso
            dc: degree of certainty
            dct: degree of contradiction

        Returns:
            Tupla (label, regions) onde:
            - label: Rótulo da região (t, f, ┬, ┴, etc)
            - regions: Dicionário de flags booleanas por região
        """
        # Calcular VSSC, VICC, VSSCT, VICCT baseados em FtC (como no MATLAB)
        vssc = ftc
        vicc = -ftc
        vssct = 1.0 - ftc
        vicct = ftc - 1.0

        # Calcular limiares efetivos
        FtC_pos = max(ftc, abs(vssc))   # dc>0
        FtC_neg = max(ftc, abs(vicc))   # dc<0
        FD_pos  = abs(vssct)  # dct>0
        FD_neg  = abs(vicct)  # dct<0

        FtC_pos_eff = max(FtC_pos - vlv, ftc)  # nunca abaixo de FtC
        FtC_neg_eff = max(FtC_neg - vlf, ftc)

        label = classify_12_regions_asymmetric(
            dc, dct,
            ThresholdsAsym(
                ftc_pos=FtC_pos_eff,
                ftc_neg=FtC_neg_eff,
                fd_pos=FD_pos,
                fd_neg=FD_neg,
            )
        )
        regs = regions_flags(label)
        return label, regs

    @staticmethod
    def evidences(dc: float, dct: float, dcr: float) -> Dict[str, float]:
        """Calcula evidências normalizadas.

        Args:
            dc: degree of certainty
            dct: degree of contradiction
            dcr: degree of real certainty

        Returns:
            Dicionário com evidências:
            - phi: Intervalo de certeza
            - muE: Evidência baseada em dc (MIE no MATLAB)
            - muECT: Evidência baseada em dct (MIEct no MATLAB)
            - muER: Evidência Real baseada em dcr (MIER no MATLAB) ⚠️ CORRIGIDO
            - phiE: Intervalo de certeza (alias)
        """
        phi = 1.0 - abs(dct)
        muE = (dc + 1.0) / 2.0
        muECT = (dct + 1.0) / 2.0
        muER = (dcr + 1.0) / 2.0  # CORRIGIDO: era (dc + dct + 1.0) / 2.0
        phiE = phi
        return {
            "phi": phi,
            "muE": muE,
            "muECT": muECT,
            "muER": muER,
            "phiE": phiE
        }

    @staticmethod
    def decision_output(muER: float, ftc: float) -> float:
        """Calcula saída de decisão baseada em muER vs FtC.

        Args:
            muER: Evidência Real (MIER)
            ftc: Certainty Control Limit (CCL)

        Returns:
            1.0 se muER > ftc
            0.0 se muER < ftc
            0.5 se muER == ftc
        """
        if muER > ftc:
            return 1.0
        elif muER < ftc:
            return 0.0
        else:
            return 0.5


    @classmethod
    def compute(cls, *, mu: float, lam: float, params: BlockParams) -> SimpleNamespace:
        """Computa todos os resultados do bloco paraconsistente.

        Workflow:
        1. Clampar inputs (mu, lam) no intervalo [0, 1]
        2. Calcular graus principais (dc, dct)
        3. Calcular geometria (d, D, dcr)
        4. Calcular evidências (muE, muECT, muER, phi)
        5. Calcular saída de decisão (decision_output)
        6. Classificar estado lógico (label)

        Args:
            mu: Grau de evidência favorável
            lam: Grau de evidência desfavorável
            params: Parâmetros do bloco (FtC, VlV, VlF, L)

        Returns:
            SimpleNamespace com todos os campos calculados
        """
        # 1. Clampar inputs
        mu = clamp01(mu)
        lam = clamp01(lam)

        # 2. Graus principais
        dc, dct = cls.core_degrees(mu, lam)

        # 3. Geometria
        d, D, dcr = cls.geometry(mu, lam, dc)

        # 4. Evidências (com muER correto)
        ev = cls.evidences(dc, dct, dcr)

        # 5. Saída de decisão
        decision = cls.decision_output(ev["muER"], params.FtC)

        # 6. Classificação
        label, regs_flag = cls.classify(params.FtC, params.VlV, params.VlF, dc, dct)

        # 7. Montar resultado completo
        complete: Complete = {
            # parâmetros
            "FtC": params.FtC,
            "VlV": params.VlV,
            "VlF": params.VlF,
            "L": params.L,
            # entradas
            "mu": mu,
            "lam": lam,
            # graus / derivados
            "dc": dc,
            "dct": dct,
            "d": d,
            "D": D,
            "dcr": dcr,
            # decisão
            "decision_output": decision,
            # classificação
            "label": label,
            "Regions": regs_flag,
            # evidências
            **ev,
        }
        return SimpleNamespace(**complete)
