
from dataclasses import (
    dataclass,
    field,
    asdict
)

from core.validators import (

    validate_login,

    validate_password,

    normalize_string
)

from core.responses import (
    ok
)

from core.logger import get_logger


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("api_contracts")


# ==================================================
# BASE DTO
# ==================================================

@dataclass
class BaseDTO:

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return asdict(self)

    # ==============================================
    # RESPONSE
    # ==============================================

    def to_response(

        self,

        mensagem="OK"
    ):

        return ok(

            mensagem=mensagem,

            dados=self.to_dict()
        )

    # ==============================================
    # SANITIZE
    # ==============================================

    def sanitize(self):

        for key, value in vars(self).items():

            if isinstance(
                value,
                str
            ):

                setattr(

                    self,

                    key,

                    normalize_string(
                        value
                    )
                )

        return self


# ==================================================
# META
# ==================================================

@dataclass
class MetaDTO:

    pagina: int = 1

    tamanho: int = 50

    total: int = 0

    total_paginas: int = 0


# ==================================================
# PAGINATED
# ==================================================

@dataclass
class PaginatedDTO:

    items: list = field(
        default_factory=list
    )

    meta: MetaDTO = field(
        default_factory=MetaDTO
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "items": [

                x.to_dict()

                if hasattr(
                    x,
                    "to_dict"
                )

                else x

                for x in self.items
            ],

            "meta": self.meta.to_dict()
        }


# ==================================================
# AUTH
# ==================================================

@dataclass
class LoginRequestDTO(BaseDTO):

    login: str = ""

    senha: str = ""

    # ==============================================
    # VALIDATE
    # ==============================================

    def validate(self):

        self.login = validate_login(
            self.login
        )

        self.senha = validate_password(
            self.senha
        )

        return self


@dataclass
class LoginResponseDTO(BaseDTO):

    sucesso: bool = False

    token: str = ""

    usuario_id: int = 0

    login: str = ""

    perfil_id: int = 0

    admin_level: int = 0


# ==================================================
# USER
# ==================================================

@dataclass
class UserDTO(BaseDTO):

    id: int = 0

    login: str = ""

    nome: str = ""

    perfil_id: int = 0

    perfil_nome: str = ""

    admin_level: int = 0

    ativo: bool = True

    # ==============================================
    # VALIDATE
    # ==============================================

    def validate(self):

        self.login = validate_login(
            self.login
        )

        self.nome = normalize_string(
            self.nome
        )

        return self


# ==================================================
# PROFILE
# ==================================================

@dataclass
class ProfileDTO(BaseDTO):

    id: int = 0

    nome: str = ""

    admin_level: int = 0

    sistema: bool = False


# ==================================================
# MENU
# ==================================================

@dataclass
class MenuDTO(BaseDTO):

    id: int = 0

    nome: str = ""

    rota: str = ""

    tipo: str = "M"

    pai_id: int = 0

    level: int = 0

    sistema: bool = False

    filhos: list = field(
        default_factory=list
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "id": self.id,

            "nome": self.nome,

            "rota": self.rota,

            "tipo": self.tipo,

            "pai_id": self.pai_id,

            "level": self.level,

            "sistema": self.sistema,

            "filhos": [

                x.to_dict()

                if hasattr(
                    x,
                    "to_dict"
                )

                else x

                for x in self.filhos
            ]
        }


# ==================================================
# EVENT
# ==================================================

@dataclass
class EventDTO(BaseDTO):

    id: int = 0

    titulo: str = ""

    descricao: str = ""

    data_evento: str = ""

    local: str = ""


# ==================================================
# DIAGNOSTICS
# ==================================================

@dataclass
class DiagnosticsDTO(BaseDTO):

    status: str = "UP"

    uptime: str = ""

    cache_items: int = 0

    cache_hit_ratio: float = 0

    scheduler_running: bool = False

    events: int = 0


# ==================================================
# ERROR
# ==================================================

@dataclass
class ErrorDTO(BaseDTO):

    sucesso: bool = False

    codigo: str = "ERROR"

    mensagem: str = "Erro."

    detalhes: str = ""


# ==================================================
# FACTORIES
# ==================================================

def create_user_dto(data):

    return UserDTO(

        id=data.get("id", 0),

        login=data.get("login", ""),

        nome=data.get("nome", ""),

        perfil_id=data.get(
            "perfil_id",
            0
        ),

        perfil_nome=data.get(
            "perfil_nome",
            ""
        ),

        admin_level=data.get(
            "admin_level",
            0
        ),

        ativo=data.get(
            "ativo",
            True
        )
    )


def create_menu_dto(data):

    return MenuDTO(

        id=data.get("id", 0),

        nome=data.get("nome", ""),

        rota=data.get(
            "rota",
            ""
        ),

        tipo=data.get(
            "tipo",
            "M"
        ),

        pai_id=data.get(
            "pai_id",
            0
        ),

        level=data.get(
            "level",
            0
        ),

        sistema=data.get(
            "sistema",
            False
        )
    )


# ==================================================
# PAGINATION FACTORY
# ==================================================

def create_paginated_dto(

    items,

    pagina=1,

    tamanho=50,

    total=0
):

    total_paginas = 0

    if tamanho > 0:

        total_paginas = (

            total // tamanho
        )

        if total % tamanho:

            total_paginas += 1

    return PaginatedDTO(

        items=items,

        meta=MetaDTO(

            pagina=pagina,

            tamanho=tamanho,

            total=total,

            total_paginas=(
                total_paginas
            )
        )
    )


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "API contracts inicializado."
)
