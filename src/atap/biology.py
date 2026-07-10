"""
biology.py — the mechanistic core of the ATAP-M8 salvage hypothesis, encoded as data.

Everything downstream (features, scoring, spatial mapping) reads its gene sets and
directional priors from here so the biology lives in exactly one place and can be
audited independently of the statistics.

------------------------------------------------------------------------------------
The hypothesis in one paragraph
------------------------------------------------------------------------------------
BH3-mimetics — venetoclax (BCL2), navitoclax (BCL2/BCL-XL), and the next-gen MCL1
inhibitors (S63845, AMG-176/AZD5991, tapotoclax) — do not kill cells directly. They
occupy the BH3-binding groove of an anti-apoptotic guardian (BCL2 / BCL-XL / MCL1),
displacing BH3-only activators and sequestered effectors. Death still has to be
executed by the pore-forming effectors BAX and BAK. If a tumor loses functional
BAX/BAK — a documented clinical resistance mechanism in relapsed AML and CLL — then
*every drug in this class fails at the same step*, no matter which guardian it targets.

ATAP (Amphipathic Tail-Anchoring Peptide, derived from the C-terminal tail-anchor of
BFL-1/BCL2A1) permeabilizes the mitochondrial membrane itself. It is the effector; it
does not need BAX/BAK and does not compete for a BH3 groove. So its predicted window
is exactly the population where the BH3-mimetic class is mechanically dead: BAX/BAK-
deficient, but with mitochondria still present and the downstream apoptosome/caspase
machinery still intact to convert membrane permeabilization into death.

That gives a two-axis map:
    - BH3-mimetic (venetoclax) predicted efficacy  — the current standard of care
    - ATAP predicted efficacy                      — the BAX-independent salvage
The clinically interesting cells are LOW on the first axis and HIGH on the second.
"""

from __future__ import annotations

# ----------------------------------------------------------------------------------
# BCL-2 family: the switch that both agents act on (differently)
# ----------------------------------------------------------------------------------

# Anti-apoptotic guardians. These are what BH3-mimetics inhibit. ATAP ignores them.
ANTIAPOPTOTIC = {
    "BCL2":    "venetoclax target; canonical guardian in CLL and BCL2-high AML",
    "BCL2L1":  "BCL-XL; navitoclax target; platelet-toxic; resistance-by-switching",
    "MCL1":    "MCL1; S63845/AMG-176/AZD5991 target; #1 venetoclax bypass in AML",
    "BCL2A1":  "BFL-1/A1; ATAP is derived from this gene's tail-anchor",
    "BCL2L2":  "BCL-W; minor guardian",
}

# Pro-apoptotic effectors. The pore-formers BH3-mimetics REQUIRE. Their loss is the
# resistance mechanism ATAP is designed to bypass.
EFFECTORS = {
    "BAX":  "primary effector; functional/genetic loss drives BH3-mimetic resistance",
    "BAK1": "BAK; redundant effector; combined BAX/BAK loss is the hard-resistance case",
    "BOK":  "minor effector; ER-associated; rarely compensates",
}

# BH3-only proteins. 'Activators' directly trigger BAX/BAK; 'sensitizers' occupy
# guardians. High activator tone = 'primed' mitochondria = responsive to BH3-mimetics.
BH3_ACTIVATORS = {
    "BCL2L11": "BIM; strongest activator; priming marker",
    "BBC3":    "PUMA; p53-driven activator",
    "BID":     "BID/tBID; activator",
}
BH3_SENSITIZERS = {
    "PMAIP1": "NOXA; selectively neutralizes MCL1 — MCL1-dependence marker",
    "BAD":    "BAD; neutralizes BCL2/BCL-XL",
    "BIK":    "BIK; sensitizer",
    "HRK":    "HRK; sensitizer",
    "BMF":    "BMF; sensitizer",
}

# ----------------------------------------------------------------------------------
# Downstream execution machinery: the SHARED bottleneck.
# Both venetoclax-induced MOMP and ATAP-induced pore-formation must funnel through
# this apparatus to produce apoptotic death. If it is silenced, a cell is resistant
# to BOTH agents — this is the 'hard escape' that ATAP does NOT rescue, and encoding
# it is what keeps the ATAP score honest (it is not a blanket 'BAX-low = kill' call).
# ----------------------------------------------------------------------------------
EXECUTION_PRO = {
    "CYCS":   "cytochrome c; released on MOMP; forms apoptosome",
    "APAF1":  "apoptosome scaffold; frequently silenced in chemoresistance",
    "CASP9":  "initiator caspase of the intrinsic pathway",
    "CASP3":  "executioner caspase",
    "CASP7":  "executioner caspase",
    "DIABLO": "SMAC; neutralizes IAPs to license caspase activity",
    "HTRA2":  "Omi/HtrA2; pro-apoptotic serine protease released on MOMP",
}
# IAPs oppose execution; high levels blunt the death signal from either agent.
EXECUTION_ANTI = {
    "XIAP":  "caspase-9/3 inhibitor; raises the threshold for both agents",
    "BIRC2": "cIAP1",
    "BIRC3": "cIAP2",
    "BIRC5": "survivin",
}

# ----------------------------------------------------------------------------------
# Mitochondrial-content markers: ATAP needs a mitochondrial target to permeabilize.
# A nuclear-encoded mitochondrial mass signature (small, robust, lineage-agnostic).
# ----------------------------------------------------------------------------------
MITO_MASS = [
    "TOMM20", "TOMM22", "TIMM23", "VDAC1", "VDAC2", "VDAC3",
    "COX4I1", "SDHA", "NDUFB8", "ATP5F1A", "CS", "HSPD1",
]

# ----------------------------------------------------------------------------------
# Directional priors: sign of each block's contribution to each drug-class score.
# +1 raises predicted efficacy, -1 lowers it, 0 = the agent is indifferent to it.
# This table is the single source of truth for what makes each axis mechanistically
# distinct — reviewers can check it against the pharmacology at a glance.
# ----------------------------------------------------------------------------------
DIRECTIONAL_PRIORS = {
    # block                venetoclax   ATAP-M8    rationale
    "bcl2_dependence":       (+1,          0),   # ATAP does not compete for the BH3 groove
    "mcl1_bclxl_backup":     (-1,          0),   # guardian-switching escapes BH3-mimetics only
    "priming_activators":    (+1,        +1),    # a primed cell dies more readily to either
    "effector_competence":  (+1,        -1),    # <-- the crux: BH3 needs BAX/BAK; ATAP shines w/o it
    "execution_competence":  (+1,        +1),    # shared downstream bottleneck
    "mito_mass":              (0,        +1),    # ATAP needs a mitochondrial target; BH3 indifferent
}

# ----------------------------------------------------------------------------------
# Known damaging events. Used to override expression when mutation data is available:
# a BAX frameshift makes a cell effector-incompetent even at normal mRNA level.
# ----------------------------------------------------------------------------------
LOSS_OF_FUNCTION_CLASSES = {
    "frameshift", "nonsense", "splice", "stop_gained", "stop_lost",
    "frame_shift_del", "frame_shift_ins", "nonsense_mutation", "splice_site",
    "start_lost", "translation_start_site",
}
# BCL2 gatekeeper mutations that reduce venetoclax binding without touching BAX/BAK —
# a resistance route ATAP is agnostic to (it never binds BCL2).
VENETOCLAX_BINDING_MUTATIONS = {"G101V", "D103Y", "D103E", "A113G", "R107_R110dup", "V156D"}


def all_genes() -> list[str]:
    """Every gene the pipeline references, de-duplicated and sorted."""
    genes: set[str] = set()
    for d in (ANTIAPOPTOTIC, EFFECTORS, BH3_ACTIVATORS, BH3_SENSITIZERS,
              EXECUTION_PRO, EXECUTION_ANTI):
        genes.update(d.keys())
    genes.update(MITO_MASS)
    return sorted(genes)


# Genes grouped into the feature 'blocks' that scoring.py consumes.
FEATURE_BLOCKS = {
    "bcl2_dependence":     ["BCL2"],
    "mcl1_bclxl_backup":   ["MCL1", "BCL2L1"],
    "priming_activators":  list(BH3_ACTIVATORS.keys()),
    "effector_competence": ["BAX", "BAK1"],
    "execution_competence": list(EXECUTION_PRO.keys()),  # anti-execution handled with a sign flip
    "mito_mass":           MITO_MASS,
}
