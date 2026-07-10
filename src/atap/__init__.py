"""
ATAP-M8 as a BAX-independent salvage therapy for BH3-mimetic-resistant blood cancers
— computational spine.

Predict which venetoclax-resistant tumors are ATAP-susceptible from BAX/BAK/priming
status (bulk: DepMap / BeatAML / TCGA), and localize where within a tumor a
BAX-independent agent is needed (spatial transcriptomics).
"""

from . import biology, features, scoring, data, spatial
from .scoring import SusceptibilityModel
from .data import Cohort

__all__ = [
    "biology", "features", "scoring", "data", "spatial",
    "SusceptibilityModel", "Cohort",
]
__version__ = "0.1.0"
