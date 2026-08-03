"""EvidenceBound DataHub Gate."""

from .core import GateReceipt, evaluate_candidate
from .pack import export_proof_pack, verify_proof_pack

__all__ = [
    "GateReceipt",
    "evaluate_candidate",
    "export_proof_pack",
    "verify_proof_pack",
]

__version__ = "0.1.0"
