"""
Módulo de governança do sistema.

Fornece componentes para conformidade com LGPD, auditoria, e políticas de segurança.
"""

from src.governance.lgpd import (
    LegalBasisEnum,
    DataSubjectRightEnum,
    ConsentRecord,
    DataSubjectRequest,
    DataProcessingRecord,
    LGPDComplianceManager,
    get_lgpd_manager
)

__all__ = [
    "LegalBasisEnum",
    "DataSubjectRightEnum",
    "ConsentRecord",
    "DataSubjectRequest",
    "DataProcessingRecord",
    "LGPDComplianceManager",
    "get_lgpd_manager"
]
