# Governança e Conformidade com a LGPD

## Visão Geral

O **Automation-Computer** foi desenvolvido com conformidade à Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018) como princípio fundamental. Este documento descreve as políticas e implementações técnicas que garantem a proteção de dados pessoais.

## Princípios LGPD Observados

### 1. Finalidade
- Dados são coletados apenas para propósitos específicos e legítimos
- Usuário é informado claramente sobre cada finalidade
- Coleta mínima necessária para a operação

### 2. Adequação
- Apenas dados compatíveis com a finalidade são processados
- Revolução periódica da necessidade de cada dado coletado

### 3. Necessidade
- Minimização de dados: coletamos o mínimo necessário
- Retenção limitada: dados são apagados quando não mais necessários

### 4. Livre Acesso
- Usuário pode acessar seus dados a qualquer momento
- Interface clara para visualização de dados armazenados

### 5. Qualidade dos Dados
- Dados são mantidos atualizados
- Mecanismos de correção disponíveis

### 6. Transparência
- Políticas claras e acessíveis
- Registro detalhado de operações (auditoria)

### 7. Segurança
- Criptografia de dados em repouso e em trânsito
- Controle de acesso baseado em papéis
- Sandboxing de execuções

### 8. Prevenção
- Medidas técnicas para prevenir vazamentos
- Rate limiting contra abuso

### 9. Não Discriminação
- Algoritmos auditados para viés
- Decisões automatizadas passíveis de revisão humana

### 10. Responsabilização e Prestação de Contas
- Logs de auditoria completos
- Documentação de processos
- DPO (Data Protection Officer) designado

## Implementações Técnicas

### Criptografia

```python
# Dados sensíveis são criptografados com Fernet (AES-128)
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()
```

### Mascaramento de Dados

```python
# Logs não expõem dados sensíveis
def mask_sensitive_data(data: str) -> str:
    CPF: ***.***.***-**
    EMAIL: ***@***.***
    TOKEN: sk-***...***
```

### Auditoria Completa

Toda ação é registrada com:
- Timestamp (ISO 8601)
- Agente (usuário/sistema)
- Ação executada
- Dados afetados (referência, não conteúdo)
- Resultado (sucesso/falha)

### Direitos do Titular

O sistema implementa interface para:

| Direito | Implementação |
|---------|---------------|
| Confirmação | Comando `--show-my-data` |
| Acesso | Exportação em JSON/CSV |
| Correção | Interface de edição |
| Anonimização | `--anonymize my-data` |
| Eliminação | `--delete my-data` |
| Portabilidade | Exportação em formato aberto |
| Revogação | Limpeza de tokens API |

## Fluxo de Dados

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Usuário   │────▶│  Automation  │────▶│   Dados     │
│             │     │   Computer   │     │Criptografados│
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Auditor   │
                    │   (Logging)  │
                    └──────────────┘
```

## Contato do DPO

**Encarregado de Proteção de Dados**
- Email: dpo@automation-computer.dev
- Resposta em até 5 dias úteis

## Atualizações

Esta política é revisada trimestralmente ou quando:
- Mudanças na legislação
- Novos recursos que coletam dados
- Solicitação de autoridade competente

## Base Legal

- **Consentimento**: Para funcionalidades opcionais
- **Execução de Contrato**: Para funcionalidades essenciais
- **Legítimo Interesse**: Para auditoria e segurança

---

*Última atualização: Julho de 2026*