#!/usr/bin/env python3
"""
BioQL Proteomics Module - v6.0.0

Quantum-enhanced proteomics analysis including:
- Protein sequence analysis
- Post-translational modification (PTM) prediction
- Protein-protein interaction (PPI) prediction
- Structure prediction
- Mass spectrometry analysis

Author: BioQL Development Team / SpectrixRD
License: MIT
"""

from typing import Optional

# Core protein analysis
try:
    from .protein_analysis import (
        analyze_protein_sequence,
        predict_protein_properties,
        classify_protein_family,
        ProteinResult,
        ProteinProperties
    )
    HAVE_PROTEIN_ANALYSIS = True
except ImportError:
    analyze_protein_sequence = None
    predict_protein_properties = None
    classify_protein_family = None
    ProteinResult = None
    ProteinProperties = None
    HAVE_PROTEIN_ANALYSIS = False

# PTM prediction
try:
    from .ptm_prediction import (
        predict_ptm_sites,
        predict_phosphorylation,
        predict_acetylation,
        predict_methylation,
        PTMSite,
        PTMResult
    )
    HAVE_PTM_PREDICTION = True
except ImportError:
    predict_ptm_sites = None
    predict_phosphorylation = None
    predict_acetylation = None
    predict_methylation = None
    PTMSite = None
    PTMResult = None
    HAVE_PTM_PREDICTION = False

# Protein-protein interactions
try:
    from .protein_interaction import (
        predict_protein_protein_interaction,
        screen_ppi_network,
        PPIResult,
        InteractionType
    )
    HAVE_PPI = True
except ImportError:
    predict_protein_protein_interaction = None
    screen_ppi_network = None
    PPIResult = None
    InteractionType = None
    HAVE_PPI = False

# Structure prediction
try:
    from .structure_prediction import (
        predict_secondary_structure,
        predict_3d_structure,
        Structure3D,
        SecondaryStructure
    )
    HAVE_STRUCTURE = True
except ImportError:
    predict_secondary_structure = None
    predict_3d_structure = None
    Structure3D = None
    SecondaryStructure = None
    HAVE_STRUCTURE = False

# Mass spectrometry
try:
    from .mass_spec import (
        analyze_mass_spectrum,
        identify_peptides,
        MSResult,
        Peptide
    )
    HAVE_MASS_SPEC = True
except ImportError:
    analyze_mass_spectrum = None
    identify_peptides = None
    MSResult = None
    Peptide = None
    HAVE_MASS_SPEC = False

# Quantum circuits for proteomics
try:
    from .quantum_proteomics import (
        secondary_structure_circuit,
        ppi_affinity_circuit,
        protein_feature_map
    )
    HAVE_QUANTUM_PROTEOMICS = True
except ImportError:
    secondary_structure_circuit = None
    ppi_affinity_circuit = None
    protein_feature_map = None
    HAVE_QUANTUM_PROTEOMICS = False

__all__ = [
    # Core analysis
    "analyze_protein_sequence",
    "predict_protein_properties",
    "classify_protein_family",
    "ProteinResult",
    "ProteinProperties",

    # PTM prediction
    "predict_ptm_sites",
    "predict_phosphorylation",
    "predict_acetylation",
    "predict_methylation",
    "PTMSite",
    "PTMResult",

    # PPI
    "predict_protein_protein_interaction",
    "screen_ppi_network",
    "PPIResult",
    "InteractionType",

    # Structure
    "predict_secondary_structure",
    "predict_3d_structure",
    "Structure3D",
    "SecondaryStructure",

    # Mass spec
    "analyze_mass_spectrum",
    "identify_peptides",
    "MSResult",
    "Peptide",

    # Quantum circuits
    "secondary_structure_circuit",
    "ppi_affinity_circuit",
    "protein_feature_map",

    # Availability flags
    "HAVE_PROTEIN_ANALYSIS",
    "HAVE_PTM_PREDICTION",
    "HAVE_PPI",
    "HAVE_STRUCTURE",
    "HAVE_MASS_SPEC",
    "HAVE_QUANTUM_PROTEOMICS",
]

__version__ = "6.0.0"
