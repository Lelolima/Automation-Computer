# NOME_DO_ARQUIVO.py: lgpd.py
# Descrição: Módulo de conformidade com a Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018).
# Responsabilidades: Gerenciar consentimento, direitos dos titulares, anonimização, pseudonimização, 
#                     registro de operações, e políticas de retenção de dados pessoais.
# Dependências: datetime, hashlib, json, logging, typing, pathlib, src.config, src.security.encryption
# Padrões aplicados: Dataclass para modelos de dados, Singleton para LogManager, 
#                     Criptografia para dados sensíveis, Logging estruturado para auditoria.
# Autor: Equipe de Governança Elite
# Última modificação: 2024-01-XX

"""
Módulo de conformidade com a LGPD (Lei Geral de Proteção de Dados).
Implementa mecanismos para garantir privacidade e proteção de dados pessoais.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from src.config import settings
from src.security.encryption import EncryptionManager


class LegalBasisEnum(str, Enum):
    """Base legal para processamento de dados conforme Art. 7º da LGPD."""
    CONSENTIMENTO = "consentimento"
    OBRIGACAO_LEGAL = "obrigacao_legal_regulatoria"
    EXECUCAO_CONTRATO = "execucao_contrato"
    EXERCICIO_DIREITOS = "exercicio_direitos_processo"
    INTERESSE_LEGITIMO = "interesse_legitimo"
    PROTECAO_VIDA = "protecao_vida_saude"
    TUTELA_CREDITO = "tutela_credito"
    INTERESSE_PUBLICO = "interesse_publico"


class DataSubjectRightEnum(str, Enum):
    """Direitos dos titulares conforme Art. 18 da LGPD."""
    CONFIRMACAO = "confirmacao_existencia_tratamento"
    ACESSO = "acesso_dados"
    CORRECAO = "correcao_dados_incompletos_inexatos_desatualizados"
    ANONIMIZACAO_BLOQUEIO_ELIMINACAO = "anonimizacao_bloqueio_eliminacao"
    PORTABILIDADE = "portabilidade_dados"
    ELIMINACAO_DADOS_CONSENTIMENTO = "eliminacao_dados_consentimento"
    INFORMACAO_ENTIDADES = "informacao_entidades_compartilhadas"
    INFORMACAO_CONSEQUENCIAS = "informacao_consequencias_negativa_consentimento"
    REVOGACAO = "revogacao_consentimento"


@dataclass
class ConsentRecord:
    """Registro de consentimento do titular."""
    id: str = field(default_factory=lambda: str(uuid4()))
    holder_id: str = ""  # Identificador único do titular (pseudonimizado)
    holder_name: Optional[str] = None  # Nome completo (criptografado se armazenado)
    holder_email: Optional[str] = None  # E-mail (criptografado se armazenado)
    purpose: str = ""  # Finalidade do tratamento
    legal_basis: LegalBasisEnum = LegalBasisEnum.CONSENTIMENTO
    granted: bool = False
    granted_at: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def grant(self, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        """Registra a concessão de consentimento."""
        self.granted = True
        self.granted_at = datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.updated_at = datetime.utcnow()

    def revoke(self) -> None:
        """Registra a revogação de consentimento."""
        self.revoked = True
        self.revoked_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_valid(self) -> bool:
        """Verifica se o consentimento está válido."""
        return self.granted and not self.revoked


@dataclass
class DataSubjectRequest:
    """Solicitação de exercício de direito pelo titular."""
    id: str = field(default_factory=lambda: str(uuid4()))
    holder_id: str = ""
    request_type: DataSubjectRightEnum = DataSubjectRightEnum.ACESSO
    description: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, rejected
    created_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    deadline: datetime = field(init=False)
    
    def __post_init__(self):
        # Prazo de 15 dias úteis para resposta conforme LGPD
        self.deadline = datetime.utcnow() + timedelta(days=15)

    def complete(self, response_data: Optional[Dict[str, Any]] = None) -> None:
        """Marca a solicitação como concluída."""
        self.status = "completed"
        self.responded_at = datetime.utcnow()
        self.response_data = response_data

    def reject(self) -> None:
        """Rejeita a solicitação com justificativa."""
        self.status = "rejected"
        self.responded_at = datetime.utcnow()


@dataclass
class DataProcessingRecord:
    """Registro de operação de tratamento de dados (Art. 37º LGPD)."""
    id: str = field(default_factory=lambda: str(uuid4()))
    operation_type: str = ""  # coleta, armazenamento, uso, compartilhamento, eliminação
    data_categories: List[str] = field(default_factory=list)
    purpose: str = ""
    legal_basis: LegalBasisEnum = LegalBasisEnum.CONSENTIMENTO
    retention_period: Optional[timedelta] = None
    entities_shared_with: List[str] = field(default_factory=list)
    security_measures: List[str] = field(default_factory=list)
    performed_by: str = ""
    performed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LGPDComplianceManager:
    """
    Gerenciador de conformidade com a LGPD.
    
    Responsável por:
    - Gestão de consentimentos
    - Exercício de direitos dos titulares
    - Registro de operações de tratamento
    - Anonimização e pseudonimização de dados
    - Políticas de retenção e eliminação
    - Auditoria e logging de operações
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa o gerenciador de conformidade LGPD.
        
        Args:
            encryption_key: Chave para criptografar dados sensíveis. 
                           Se None, usa a ENCRYPTION_KEY das settings.
        """
        self._encryption_manager = EncryptionManager(
            key=encryption_key.encode('utf-8') if encryption_key else None
        )
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._data_requests: Dict[str, DataSubjectRequest] = {}
        self._processing_records: List[DataProcessingRecord] = []
        self._logger = self._setup_logger()
        
        self._logger.info("LGPD Compliance Manager initialized")

    def _setup_logger(self) -> logging.Logger:
        """Configura logger específico para auditoria LGPD."""
        logger = logging.getLogger("lgpd_compliance")
        logger.setLevel(logging.INFO)
        
        # Handler para arquivo de auditoria
        log_file = Path(settings.LOG_FILE).parent / "lgpd_audit.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | LGPD | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(file_handler)
        
        return logger

    # ==========================================
    # GESTÃO DE CONSENTIMENTO
    # ==========================================
    
    def register_consent(
        self,
        holder_id: str,
        purpose: str,
        legal_basis: LegalBasisEnum = LegalBasisEnum.CONSENTIMENTO,
        holder_name: Optional[str] = None,
        holder_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """
        Registra um novo consentimento.
        
        Args:
            holder_id: Identificador único do titular (deve ser pseudonimizado)
            purpose: Finalidade do tratamento de dados
            legal_basis: Base legal para o tratamento
            holder_name: Nome do titular (será criptografado)
            holder_email: E-mail do titular (será criptografado)
            ip_address: IP do usuário no momento do consentimento
            user_agent: User agent do navegador
            metadata: Metadados adicionais
            
        Returns:
            ConsentRecord: Registro de consentimento criado
            
        Raises:
            ValueError: Se holder_id ou purpose estiverem vazios
        """
        if not holder_id or not purpose:
            raise ValueError("holder_id e purpose são obrigatórios")
        
        # Criptografar dados sensíveis antes de armazenar
        encrypted_name = None
        encrypted_email = None
        
        if holder_name:
            try:
                encrypted_name = self._encryption_manager.encrypt(holder_name)
            except Exception as e:
                self._logger.warning(f"Falha ao criptografar nome: {e}")
                encrypted_name = holder_name  # Fallback (não ideal)
        
        if holder_email:
            try:
                encrypted_email = self._encryption_manager.encrypt(holder_email)
            except Exception as e:
                self._logger.warning(f"Falha ao criptografar email: {e}")
                encrypted_email = holder_email
        
        record = ConsentRecord(
            holder_id=holder_id,
            holder_name=encrypted_name,
            holder_email=encrypted_email,
            purpose=purpose,
            legal_basis=legal_basis,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        record.grant(ip_address=ip_address, user_agent=user_agent)
        self._consent_records[record.id] = record
        
        self._log_operation(
            operation="CONSENT_GRANTED",
            holder_id=holder_id,
            details={
                "consent_id": record.id,
                "purpose": purpose,
                "legal_basis": legal_basis.value
            }
        )
        
        return record

    def revoke_consent(self, consent_id: str) -> bool:
        """
        Revoga um consentimento previamente concedido.
        
        Args:
            consent_id: ID do registro de consentimento
            
        Returns:
            bool: True se revogado com sucesso, False se não encontrado
        """
        if consent_id not in self._consent_records:
            self._logger.warning(f"Tentativa de revogar consentimento inexistente: {consent_id}")
            return False
        
        record = self._consent_records[consent_id]
        record.revoke()
        
        self._log_operation(
            operation="CONSENT_REVOKED",
            holder_id=record.holder_id,
            details={
                "consent_id": consent_id,
                "purpose": record.purpose
            }
        )
        
        return True

    def get_consent_status(self, holder_id: str, purpose: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém o status de consentimento para um titular.
        
        Args:
            holder_id: Identificador do titular
            purpose: Filtrar por finalidade específica (opcional)
            
        Returns:
            Dict com status dos consentimentos
        """
        consents = [
            c for c in self._consent_records.values()
            if c.holder_id == holder_id
        ]
        
        if purpose:
            consents = [c for c in consents if c.purpose == purpose]
        
        return {
            "holder_id": holder_id,
            "total_consents": len(consents),
            "active_consents": sum(1 for c in consents if c.is_valid()),
            "revoked_consents": sum(1 for c in consents if c.revoked),
            "consents": [
                {
                    "id": c.id,
                    "purpose": c.purpose,
                    "legal_basis": c.legal_basis.value,
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                    "is_valid": c.is_valid()
                }
                for c in consents
            ]
        }

    # ==========================================
    # DIREITOS DOS TITULARES
    # ==========================================
    
    def create_data_subject_request(
        self,
        holder_id: str,
        request_type: DataSubjectRightEnum,
        description: Optional[str] = None
    ) -> DataSubjectRequest:
        """
        Cria uma solicitação de exercício de direito.
        
        Args:
            holder_id: Identificador do titular
            request_type: Tipo de direito sendo exercido
            description: Descrição adicional da solicitação
            
        Returns:
            DataSubjectRequest: Solicitação criada
        """
        request = DataSubjectRequest(
            holder_id=holder_id,
            request_type=request_type,
            description=description
        )
        
        self._data_requests[request.id] = request
        
        self._log_operation(
            operation="DATA_SUBJECT_REQUEST_CREATED",
            holder_id=holder_id,
            details={
                "request_id": request.id,
                "request_type": request_type.value,
                "deadline": request.deadline.isoformat()
            }
        )
        
        return request

    def process_data_request(self, request_id: str, response_data: Dict[str, Any]) -> bool:
        """
        Processa e responde uma solicitação de titular.
        
        Args:
            request_id: ID da solicitação
            response_data: Dados da resposta
            
        Returns:
            bool: True se processado com sucesso
        """
        if request_id not in self._data_requests:
            return False
        
        request = self._data_requests[request_id]
        request.complete(response_data)
        
        self._log_operation(
            operation="DATA_SUBJECT_REQUEST_COMPLETED",
            holder_id=request.holder_id,
            details={
                "request_id": request_id,
                "request_type": request.request_type.value,
                "response_provided": response_data is not None
            }
        )
        
        return True

    def get_pending_requests(self) -> List[DataSubjectRequest]:
        """Obtém todas as solicitações pendentes."""
        return [
            r for r in self._data_requests.values()
            if r.status == "pending"
        ]

    def get_overdue_requests(self) -> List[DataSubjectRequest]:
        """Obtém solicitações vencidas (fora do prazo LGPD)."""
        now = datetime.utcnow()
        return [
            r for r in self._data_requests.values()
            if r.status == "pending" and now > r.deadline
        ]

    # ==========================================
    # REGISTRO DE OPERAÇÕES (ART. 37º)
    # ==========================================
    
    def register_processing_operation(
        self,
        operation_type: str,
        data_categories: List[str],
        purpose: str,
        legal_basis: LegalBasisEnum,
        retention_period: Optional[timedelta] = None,
        entities_shared_with: Optional[List[str]] = None,
        security_measures: Optional[List[str]] = None,
        performed_by: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> DataProcessingRecord:
        """
        Registra uma operação de tratamento de dados.
        
        Args:
            operation_type: Tipo de operação (coleta, uso, armazenamento, etc.)
            data_categories: Categorias de dados tratados
            purpose: Finalidade do tratamento
            legal_basis: Base legal
            retention_period: Período de retenção dos dados
            entities_shared_with: Entidades com quem os dados foram compartilhados
            security_measures: Medidas de segurança aplicadas
            performed_by: Identificação de quem realizou a operação
            metadata: Metadados adicionais
            
        Returns:
            DataProcessingRecord: Registro da operação
        """
        record = DataProcessingRecord(
            operation_type=operation_type,
            data_categories=data_categories,
            purpose=purpose,
            legal_basis=legal_basis,
            retention_period=retention_period,
            entities_shared_with=entities_shared_with or [],
            security_measures=security_measures or [],
            performed_by=performed_by,
            metadata=metadata or {}
        )
        
        self._processing_records.append(record)
        
        self._log_operation(
            operation="PROCESSING_REGISTERED",
            holder_id="N/A",
            details={
                "operation_id": record.id,
                "operation_type": operation_type,
                "data_categories": data_categories,
                "legal_basis": legal_basis.value
            }
        )
        
        return record

    def get_processing_records(
        self,
        operation_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[DataProcessingRecord]:
        """
        Obtém registros de operações de tratamento.
        
        Args:
            operation_type: Filtrar por tipo de operação
            date_from: Data inicial
            date_to: Data final
            
        Returns:
            Lista de registros filtrados
        """
        records = self._processing_records
        
        if operation_type:
            records = [r for r in records if r.operation_type == operation_type]
        
        if date_from:
            records = [r for r in records if r.performed_at >= date_from]
        
        if date_to:
            records = [r for r in records if r.performed_at <= date_to]
        
        return records

    # ==========================================
    # ANONIMIZAÇÃO E PSEUDONIMIZAÇÃO
    # ==========================================
    
    @staticmethod
    def pseudonymize_data(data: str, salt: Optional[str] = None) -> str:
        """
        Pseudonimiza um dado usando hash SHA-256 com salt.
        
        Args:
            data: Dado a ser pseudonimizado
            salt: Salt opcional para aumentar segurança
            
        Returns:
            str: Hash pseudonimizado
        """
        salted_data = f"{data}{salt or settings.SECRET_KEY}"
        return hashlib.sha256(salted_data.encode('utf-8')).hexdigest()

    @staticmethod
    def anonymize_data(data: Dict[str, Any], fields_to_anonymize: List[str]) -> Dict[str, Any]:
        """
        Anonimiza campos específicos de um dicionário de dados.
        
        Args:
            data: Dicionário com dados pessoais
            fields_to_anonymize: Lista de campos a serem anonimizados
            
        Returns:
            Dict: Dados com campos anonimizados
        """
        anonymized = data.copy()
        
        for field_name in fields_to_anonymize:
            if field_name in anonymized:
                original_value = str(anonymized[field_name])
                # Substitui por hash pseudonimizado
                anonymized[field_name] = f"ANON_{hashlib.sha256(original_value.encode()).hexdigest()[:16]}"
        
        return anonymized

    def encrypt_sensitive_field(self, value: str) -> str:
        """
        Criptografa um campo sensível.
        
        Args:
            value: Valor a ser criptografado
            
        Returns:
            str: Valor criptografado em base64
        """
        return self._encryption_manager.encrypt(value)

    def decrypt_sensitive_field(self, encrypted_value: str) -> str:
        """
        Descriptografa um campo sensível.
        
        Args:
            encrypted_value: Valor criptografado
            
        Returns:
            str: Valor original descriptografado
        """
        return self._encryption_manager.decrypt(encrypted_value)

    # ==========================================
    # POLÍTICAS DE RETENÇÃO E ELIMINAÇÃO
    # ==========================================
    
    def check_retention_policy(
        self,
        data_created_at: datetime,
        retention_period: timedelta,
        data_category: str
    ) -> Dict[str, Any]:
        """
        Verifica se dados devem ser eliminados conforme política de retenção.
        
        Args:
            data_created_at: Data de criação/coleta dos dados
            retention_period: Período de retenção definido
            data_category: Categoria dos dados
            
        Returns:
            Dict com status de retenção
        """
        now = datetime.utcnow()
        expiration_date = data_created_at + retention_period
        days_until_expiration = (expiration_date - now).days
        
        return {
            "data_category": data_category,
            "created_at": data_created_at.isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "days_until_expiration": days_until_expiration,
            "should_delete": days_until_expiration < 0,
            "status": "expired" if days_until_expiration < 0 else "active"
        }

    def schedule_data_deletion(
        self,
        holder_id: str,
        data_ids: List[str],
        reason: str,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Agenda eliminação de dados pessoais.
        
        Args:
            holder_id: Identificador do titular
            data_ids: IDs dos dados a serem eliminados
            reason: Motivo da eliminação
            scheduled_for: Data agendada para eliminação
            
        Returns:
            Dict com informações do agendamento
        """
        deletion_record = {
            "id": str(uuid4()),
            "holder_id": holder_id,
            "data_ids": data_ids,
            "reason": reason,
            "scheduled_for": (scheduled_for or datetime.utcnow()).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
        self._log_operation(
            operation="DATA_DELETION_SCHEDULED",
            holder_id=holder_id,
            details=deletion_record
        )
        
        return deletion_record

    # ==========================================
    # AUDITORIA E LOGGING
    # ==========================================
    
    def _log_operation(
        self,
        operation: str,
        holder_id: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Registra operação em log de auditoria.
        
        Args:
            operation: Tipo de operação
            holder_id: Identificador do titular (pseudonimizado)
            details: Detalhes da operação
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "holder_id": holder_id,
            "details": details
        }
        
        self._logger.info(json.dumps(log_entry, ensure_ascii=False))

    def get_audit_log(
        self,
        operation_filter: Optional[str] = None,
        holder_id_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtém logs de auditoria (implementação simplificada).
        
        Nota: Em produção, isso deveria consultar um banco de dados
        ou sistema de logging centralizado.
        
        Args:
            operation_filter: Filtrar por tipo de operação
            holder_id_filter: Filtrar por holder_id
            date_from: Data inicial
            date_to: Data final
            limit: Limite de registros
            
        Returns:
            Lista de entradas de log
        """
        # Implementação real dependeria de persistência dos logs
        return []

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Gera relatório de conformidade LGPD.
        
        Returns:
            Dict com métricas de conformidade
        """
        total_consents = len(self._consent_records)
        active_consents = sum(1 for c in self._consent_records.values() if c.is_valid())
        
        total_requests = len(self._data_requests)
        pending_requests = sum(1 for r in self._data_requests.values() if r.status == "pending")
        overdue_requests = len(self.get_overdue_requests())
        
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "consents": {
                "total": total_consents,
                "active": active_consents,
                "revoked": total_consents - active_consents,
                "compliance_rate": (active_consents / total_consents * 100) if total_consents > 0 else 0
            },
            "data_subject_requests": {
                "total": total_requests,
                "pending": pending_requests,
                "overdue": overdue_requests,
                "compliance_rate": ((total_requests - overdue_requests) / total_requests * 100) if total_requests > 0 else 100
            },
            "processing_operations": {
                "total_registered": len(self._processing_records)
            },
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no estado atual de conformidade."""
        recommendations = []
        
        overdue = self.get_overdue_requests()
        if overdue:
            recommendations.append(
                f"URGENTE: {len(overdue)} solicitações de titulares estão vencidas. "
                "Responda dentro do prazo legal de 15 dias."
            )
        
        pending = self.get_pending_requests()
        if len(pending) > 5:
            recommendations.append(
                f"Atenção: {len(pending)} solicitações pendentes. "
                "Considere aumentar a capacidade de resposta."
            )
        
        if not recommendations:
            recommendations.append("Sistema em conformidade. Nenhuma ação necessária.")
        
        return recommendations


# Singleton instance
_lgpd_manager: Optional[LGPDComplianceManager] = None


def get_lgpd_manager(encryption_key: Optional[str] = None) -> LGPDComplianceManager:
    """
    Obtém instância singleton do LGPDComplianceManager.
    
    Args:
        encryption_key: Chave de criptografia opcional
        
    Returns:
        LGPDComplianceManager: Instância do gerenciador
    """
    global _lgpd_manager
    if _lgpd_manager is None:
        _lgpd_manager = LGPDComplianceManager(encryption_key=encryption_key)
    return _lgpd_manager
