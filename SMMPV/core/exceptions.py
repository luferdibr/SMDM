
from core.logger import get_logger


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("exceptions")


# ==================================================
# BASE
# ==================================================

class SMMPVError(Exception):
    """
    Exceção base do sistema.
    """

    codigo = "SMMPV_ERROR"

    status = "ERROR"

    log_level = "error"

    def __init__(

        self,

        mensagem="Erro interno.",

        detalhes=None,

        dados=None
    ):

        super().__init__(mensagem)

        self.mensagem = str(mensagem)

        self.detalhes = detalhes

        self.dados = dados

    # ==============================================
    # SERIALIZAÇÃO
    # ==============================================

    def to_dict(self):

        return {

            "sucesso": False,

            "codigo": self.codigo,

            "mensagem": self.mensagem,

            "detalhes": self.detalhes,

            "dados": self.dados
        }

    # ==============================================
    # STRING
    # ==============================================

    def __str__(self):

        return self.mensagem

    # ==============================================
    # LOG
    # ==============================================

    def registrar_log(self):

        try:

            texto = (

                f"{self.codigo} | "
                f"{self.mensagem}"
            )

            if self.log_level == "warning":

                logger.warning(texto)

            elif self.log_level == "critical":

                logger.critical(texto)

            elif self.log_level == "exception":

                logger.exception(texto)

            else:

                logger.error(texto)

        except Exception:
            pass


# ==================================================
# VALIDATION
# ==================================================

class ValidationError(SMMPVError):

    codigo = "VALIDATION_ERROR"

    status = "WARNING"

    log_level = "warning"

    def __init__(

        self,

        mensagem="Dados inválidos.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# AUTHENTICATION
# ==================================================

class AuthenticationError(SMMPVError):

    codigo = "AUTH_ERROR"

    status = "WARNING"

    log_level = "warning"

    def __init__(

        self,

        mensagem="Falha autenticação.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# PERMISSION
# ==================================================

class PermissionDeniedError(SMMPVError):

    codigo = "PERMISSION_DENIED"

    status = "WARNING"

    log_level = "warning"

    def __init__(

        self,

        mensagem="Acesso negado.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# NOT FOUND
# ==================================================

class NotFoundError(SMMPVError):

    codigo = "NOT_FOUND"

    status = "WARNING"

    log_level = "warning"

    def __init__(

        self,

        mensagem="Registro não encontrado.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# CONFLICT
# ==================================================

class ConflictError(SMMPVError):

    codigo = "CONFLICT"

    status = "WARNING"

    log_level = "warning"

    def __init__(

        self,

        mensagem="Conflito operacional.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# DATABASE
# ==================================================

class DatabaseError(SMMPVError):

    codigo = "DATABASE_ERROR"

    status = "ERROR"

    log_level = "exception"

    def __init__(

        self,

        mensagem="Erro banco dados.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# INSTALL
# ==================================================

class InstallError(SMMPVError):

    codigo = "INSTALL_ERROR"

    status = "CRITICAL"

    log_level = "critical"

    def __init__(

        self,

        mensagem="Falha instalação.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# CONFIG
# ==================================================

class ConfigError(SMMPVError):

    codigo = "CONFIG_ERROR"

    status = "CRITICAL"

    log_level = "critical"

    def __init__(

        self,

        mensagem="Configuração inválida.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# SYSTEM
# ==================================================

class SystemError(SMMPVError):

    codigo = "SYSTEM_ERROR"

    status = "CRITICAL"

    log_level = "exception"

    def __init__(

        self,

        mensagem="Erro interno sistema.",

        detalhes=None,

        dados=None
    ):

        super().__init__(
            mensagem,
            detalhes,
            dados
        )


# ==================================================
# HELPERS
# ==================================================

def raise_validation(
    mensagem,
    detalhes=None
):

    raise ValidationError(
        mensagem,
        detalhes
    )


def raise_auth(
    mensagem,
    detalhes=None
):

    raise AuthenticationError(
        mensagem,
        detalhes
    )


def raise_permission(
    mensagem,
    detalhes=None
):

    raise PermissionDeniedError(
        mensagem,
        detalhes
    )


def raise_not_found(
    mensagem,
    detalhes=None
):

    raise NotFoundError(
        mensagem,
        detalhes
    )


def raise_conflict(
    mensagem,
    detalhes=None
):

    raise ConflictError(
        mensagem,
        detalhes
    )


def raise_database(
    mensagem,
    detalhes=None
):

    raise DatabaseError(
        mensagem,
        detalhes
    )


def raise_install(
    mensagem,
    detalhes=None
):

    raise InstallError(
        mensagem,
        detalhes
    )


def raise_config(
    mensagem,
    detalhes=None
):

    raise ConfigError(
        mensagem,
        detalhes
    )


def raise_system(
    mensagem,
    detalhes=None
):

    raise SystemError(
        mensagem,
        detalhes
    )


# ==================================================
# RESPONSE
# ==================================================

def exception_to_response(ex):

    try:

        if isinstance(
            ex,
            SMMPVError
        ):

            ex.registrar_log()

            return ex.to_dict()

        logger.exception(
            "UNHANDLED ERROR"
        )

        return {

            "sucesso": False,

            "codigo": "UNHANDLED_ERROR",

            "mensagem": str(ex),

            "detalhes": None,

            "dados": None
        }

    except Exception:

        return {

            "sucesso": False,

            "codigo": "FATAL_EXCEPTION",

            "mensagem": "Erro crítico.",

            "detalhes": None,

            "dados": None
        }
