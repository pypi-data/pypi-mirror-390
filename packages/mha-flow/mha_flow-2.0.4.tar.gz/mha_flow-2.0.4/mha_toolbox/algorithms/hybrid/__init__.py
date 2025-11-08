"""
Hybrid Metaheuristic Algorithms Package
======================================

This package contains hybrid algorithms that combine multiple optimization strategies
for enhanced performance and robustness.

Each hybrid algorithm is in its own file for better maintainability.
"""

# Import existing hybrids
from .pso_ga_hybrid import PSO_GA_Hybrid
from .woa_sma_hybrid import WOA_SMA_Hybrid
from .ga_sa_hybrid import GeneticSimulatedAnnealingHybrid
from .de_pso_hybrid import DifferentialEvolutionPSOHybrid
from .abc_de_hybrid import ABC_DE_Hybrid
from .gwo_pso_hybrid import GWO_PSO_Hybrid
from .woa_ga_hybrid import WOA_GA_Hybrid
from .sma_de_hybrid import SMA_DE_Hybrid
from .fa_ga_hybrid import FA_GA_Hybrid
from .aco_pso_hybrid import ACO_PSO_Hybrid
from .sa_pso_hybrid import SA_PSO_Hybrid
from .gwo_de_hybrid import GWO_DE_Hybrid

# Import new hybrids (individual files)
from .fa_de_hybrid import FA_DE_Hybrid
from .cs_ga_hybrid import CS_GA_Hybrid
from .alo_pso_hybrid import ALO_PSO_Hybrid
from .ssa_de_hybrid import SSA_DE_Hybrid
from .mfo_de_hybrid import MFO_DE_Hybrid
from .da_ga_hybrid import DA_GA_Hybrid
from .fpa_ga_hybrid import FPA_GA_Hybrid
from .hs_de_hybrid import HS_DE_Hybrid
from .kh_pso_hybrid import KH_PSO_Hybrid
from .ts_ga_hybrid import TS_GA_Hybrid

# Import 2025 new advanced hybrids
from .gwo_woa_hybrid import GWO_WOA_Hybrid
from .pso_sca_hybrid import PSO_SCA_Hybrid
from .abc_gwo_hybrid import ABC_GWO_Hybrid
from .adaptive_multi_strategy import Adaptive_Multi_Strategy_Hybrid

__all__ = [
    # Existing hybrids
    'PSO_GA_Hybrid',
    'WOA_SMA_Hybrid',
    'GeneticSimulatedAnnealingHybrid',
    'DifferentialEvolutionPSOHybrid',
    'ABC_DE_Hybrid',
    'GWO_PSO_Hybrid',
    'WOA_GA_Hybrid',
    'SMA_DE_Hybrid',
    'FA_GA_Hybrid',
    'GA_SA_Hybrid',
    'DE_PSO_Hybrid',
    'ACO_PSO_Hybrid',
    'SA_PSO_Hybrid',
    'GWO_DE_Hybrid',
    # New individual hybrids
    'FA_DE_Hybrid',
    'CS_GA_Hybrid',
    'ALO_PSO_Hybrid',
    'SSA_DE_Hybrid',
    'MFO_DE_Hybrid',
    'DA_GA_Hybrid',
    'FPA_GA_Hybrid',
    'HS_DE_Hybrid',
    'KH_PSO_Hybrid',
    'TS_GA_Hybrid',
    # 2025 advanced hybrids
    'GWO_WOA_Hybrid',
    'PSO_SCA_Hybrid',
    'ABC_GWO_Hybrid',
    'Adaptive_Multi_Strategy_Hybrid',
]

# Aliases for convenience
GA_SA_Hybrid = GeneticSimulatedAnnealingHybrid
DE_PSO_Hybrid = DifferentialEvolutionPSOHybrid

# Algorithm mapping for easy access
HYBRID_ALGORITHMS = {
    'PSO_GA_Hybrid': PSO_GA_Hybrid,
    'WOA_SMA_Hybrid': WOA_SMA_Hybrid,
    'GeneticSimulatedAnnealingHybrid': GeneticSimulatedAnnealingHybrid,
    'DifferentialEvolutionPSOHybrid': DifferentialEvolutionPSOHybrid,
    'ABC_DE_Hybrid': ABC_DE_Hybrid,
    'GWO_PSO_Hybrid': GWO_PSO_Hybrid,
    'WOA_GA_Hybrid': WOA_GA_Hybrid,
    'SMA_DE_Hybrid': SMA_DE_Hybrid,
    'FA_GA_Hybrid': FA_GA_Hybrid,
    'ACO_PSO_Hybrid': ACO_PSO_Hybrid,
    'SA_PSO_Hybrid': SA_PSO_Hybrid,
    'GWO_DE_Hybrid': GWO_DE_Hybrid,
    'FA_DE_Hybrid': FA_DE_Hybrid,
    'CS_GA_Hybrid': CS_GA_Hybrid,
    'ALO_PSO_Hybrid': ALO_PSO_Hybrid,
    'SSA_DE_Hybrid': SSA_DE_Hybrid,
    'MFO_DE_Hybrid': MFO_DE_Hybrid,
    'DA_GA_Hybrid': DA_GA_Hybrid,
    'FPA_GA_Hybrid': FPA_GA_Hybrid,
    'HS_DE_Hybrid': HS_DE_Hybrid,
    'KH_PSO_Hybrid': KH_PSO_Hybrid,
    'TS_GA_Hybrid': TS_GA_Hybrid,
    # 2025 advanced hybrids
    'GWO_WOA_Hybrid': GWO_WOA_Hybrid,
    'PSO_SCA_Hybrid': PSO_SCA_Hybrid,
    'ABC_GWO_Hybrid': ABC_GWO_Hybrid,
    'Adaptive_Multi_Strategy_Hybrid': Adaptive_Multi_Strategy_Hybrid,
    # User-friendly aliases
    'AMSHA': Adaptive_Multi_Strategy_Hybrid,
    'GWO_WOA': GWO_WOA_Hybrid,
    'PSO_SCA': PSO_SCA_Hybrid,
    'ABC_GWO': ABC_GWO_Hybrid,
}