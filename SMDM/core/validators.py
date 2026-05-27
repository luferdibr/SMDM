
import re
from decimal import Decimal

from core.logger import get_logger

from core.exceptions import (
    ValidationError
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("validators")


# ==================================================
# CONSTANTS
# ==================================================

LOGIN_REGEX = r"^[a-zA-Z0-9_.-]+$"

ROTA_REGEX = r"^[a-z0-9_]+$"

EMAIL_REGEX = (

    r"^[a-zA-Z0-9._%+-]+"
    r"@[a-zA-Z0-9.-]+"
    r"\.[a-zA-Z]{2,}$"
)


# ==================================================
# STRING
# ==================================================

def normalize_string(

    valor,

    trim=True,

    upper=False,

    lower=False,

    max_length=None
):

    if valor is None:

        return ""

    try:

        valor = str(valor)

    except Exception:

        valor = ""

    if trim:

        valor = valor.strip()

    if upper:

        valor = valor.upper()

    if lower:

        valor = valor.lower()

    if max_length:

        valor = valor[:max_length]

    return valor


# ==================================================
# REQUIRED
# ==================================================

def required(

    valor,

    campo="Campo"
):

    texto = normalize_string(valor)

    if not texto:

        raise ValidationError(
            f"{campo} obrigatório."
        )

    return texto


# ==================================================
# MIN LENGTH
# ==================================================

def min_length(

    valor,

    tamanho,

    campo="Campo"
):

    valor = normalize_string(valor)

    if len(valor) < int(tamanho):

        raise ValidationError(

            (
                f"{campo} deve possuir "
                f"mínimo de {tamanho} caracteres."
            )
        )

    return valor


# ==================================================
# MAX LENGTH
# ==================================================

def max_length(

    valor,

    tamanho,

    campo="Campo"
):

    valor = normalize_string(valor)

    if len(valor) > int(tamanho):

        raise ValidationError(

            (
                f"{campo} deve possuir "
                f"máximo de {tamanho} caracteres."
            )
        )

    return valor


# ==================================================
# EXACT LENGTH
# ==================================================

def exact_length(

    valor,

    tamanho,

    campo="Campo"
):

    valor = normalize_string(valor)

    if len(valor) != int(tamanho):

        raise ValidationError(

            (
                f"{campo} deve possuir "
                f"{tamanho} caracteres."
            )
        )

    return valor


# ==================================================
# INTEGER
# ==================================================

def to_int(

    valor,

    campo="Valor",

    minimo=None,

    maximo=None,

    default=None
):

    try:

        numero = int(valor)

    except Exception:

        if default is not None:

            return default

        raise ValidationError(
            f"{campo} inválido."
        )

    if minimo is not None:

        if numero < minimo:

            raise ValidationError(

                (
                    f"{campo} deve ser "
                    f"maior ou igual a {minimo}."
                )
            )

    if maximo is not None:

        if numero > maximo:

            raise ValidationError(

                (
                    f"{campo} deve ser "
                    f"menor ou igual a {maximo}."
                )
            )

    return numero


# ==================================================
# DECIMAL
# ==================================================

def to_decimal(

    valor,

    campo="Valor",

    minimo=None,

    maximo=None,

    default=None
):

    try:

        numero = Decimal(str(valor))

    except Exception:

        if default is not None:

            return default

        raise ValidationError(
            f"{campo} inválido."
        )

    if minimo is not None:

        if numero < Decimal(str(minimo)):

            raise ValidationError(

                (
                    f"{campo} deve ser "
                    f"maior ou igual a {minimo}."
                )
            )

    if maximo is not None:

        if numero > Decimal(str(maximo)):

            raise ValidationError(

                (
                    f"{campo} deve ser "
                    f"menor ou igual a {maximo}."
                )
            )

    return numero


# ==================================================
# BOOLEAN
# ==================================================

def to_bool(

    valor,

    default=False
):

    if valor in (
        True,
        1,
        "1",
        "true",
        "TRUE",
        "sim",
        "SIM"
    ):

        return True

    if valor in (
        False,
        0,
        "0",
        "false",
        "FALSE",
        "nao",
        "NÃO",
        "não"
    ):

        return False

    return bool(default)


# ==================================================
# LOGIN
# ==================================================

def validate_login(

    login,

    min_chars=3,

    max_chars=50
):

    login = normalize_string(

        login,

        trim=True,

        lower=True
    )

    required(login, "Login")

    min_length(
        login,
        min_chars,
        "Login"
    )

    max_length(
        login,
        max_chars,
        "Login"
    )

    if not re.match(
        LOGIN_REGEX,
        login
    ):

        raise ValidationError(

            (
                "Login possui "
                "caracteres inválidos."
            )
        )

    return login


# ==================================================
# PASSWORD
# ==================================================

def validate_password(

    senha,

    min_chars=6,

    max_chars=120
):

    senha = normalize_string(
        senha
    )

    required(senha, "Senha")

    min_length(
        senha,
        min_chars,
        "Senha"
    )

    max_length(
        senha,
        max_chars,
        "Senha"
    )

    return senha


# ==================================================
# EMAIL
# ==================================================

def validate_email(email):

    email = normalize_string(

        email,

        trim=True,

        lower=True
    )

    required(email, "E-mail")

    if not re.match(
        EMAIL_REGEX,
        email
    ):

        raise ValidationError(
            "E-mail inválido."
        )

    return email


# ==================================================
# ROUTE
# ==================================================

def validate_route(

    rota,

    required_route=False
):

    rota = normalize_string(

        rota,

        trim=True,

        lower=True
    )

    if not rota:

        if required_route:

            raise ValidationError(
                "Rota obrigatória."
            )

        return None

    if not re.match(
        ROTA_REGEX,
        rota
    ):

        raise ValidationError(

            (
                "Rota inválida. "
                "Use apenas "
                "a-z 0-9 _"
            )
        )

    return rota


# ==================================================
# MENU TYPE
# ==================================================

def validate_menu_type(tipo):

    tipo = normalize_string(
        tipo,
        upper=True
    )

    if tipo not in (
        "T",
        "S",
        "M"
    ):

        raise ValidationError(
            "Tipo menu inválido."
        )

    return tipo


# ==================================================
# ADMIN LEVEL
# ==================================================

def validate_admin_level(

    valor,

    minimo=0,

    maximo=100
):

    return to_int(

        valor,

        campo="AdminLevel",

        minimo=minimo,

        maximo=maximo
    )


# ==================================================
# LIST
# ==================================================

def validate_list(

    valor,

    campo="Lista"
):

    if valor is None:

        return []

    if not isinstance(
        valor,
        list
    ):

        raise ValidationError(
            f"{campo} inválida."
        )

    return valor


# ==================================================
# DICT
# ==================================================

def validate_dict(

    valor,

    campo="Objeto"
):

    if valor is None:

        return {}

    if not isinstance(
        valor,
        dict
    ):

        raise ValidationError(
            f"{campo} inválido."
        )

    return valor


# ==================================================
# DATE
# ==================================================

def validate_date_string(

    valor,

    campo="Data"
):

    valor = normalize_string(valor)

    required(valor, campo)

    if not re.match(
        r"^\d{4}-\d{2}-\d{2}$",
        valor
    ):

        raise ValidationError(
            f"{campo} inválida."
        )

    return valor


# ==================================================
# SAFE TRIM
# ==================================================

def safe_trim(

    valor,

    tamanho
):

    valor = normalize_string(valor)

    return valor[:int(tamanho)]


# ==================================================
# EMPTY
# ==================================================

def is_empty(valor):

    if valor is None:
        return True

    if isinstance(
        valor,
        str
    ):

        return not valor.strip()

    if isinstance(
        valor,
        (
            list,
            dict,
            tuple,
            set
        )
    ):

        return len(valor) == 0

    return False


# ==================================================
# NOT EMPTY
# ==================================================

def not_empty(

    valor,

    campo="Campo"
):

    if is_empty(valor):

        raise ValidationError(
            f"{campo} vazio."
        )

    return valor
