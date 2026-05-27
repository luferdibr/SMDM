
import base64
import hashlib
import hmac
import os
import secrets
import string

from core.logger import get_logger

from core.exceptions import (
    ValidationError,
    AuthenticationError
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("security")


# ==================================================
# CONFIG
# ==================================================

PBKDF2_ITERATIONS = 120000

SALT_SIZE = 16

HASH_NAME = "sha256"

PASSWORD_PREFIX = "PBKDF2"

TOKEN_SIZE = 32

LEGACY_SHA256_SIZE = 64


# ==================================================
# HELPERS
# ==================================================

def normalize_login(login):

    if login is None:
        return ""

    return str(login).strip().lower()


def sanitize_text(valor):

    if valor is None:
        return ""

    texto = str(valor)

    texto = texto.replace("\x00", "")

    return texto.strip()


# ==================================================
# SECRET MASK
# ==================================================

def mask_secret(

    valor,

    visible=4
):

    texto = sanitize_text(valor)

    if not texto:
        return ""

    if len(texto) <= visible:

        return "*" * len(texto)

    return (

        "*" * (
            len(texto) - visible
        )

        +

        texto[-visible:]
    )


# ==================================================
# RANDOM TOKEN
# ==================================================

def generate_token(

    tamanho=TOKEN_SIZE
):

    return secrets.token_urlsafe(
        tamanho
    )


# ==================================================
# RANDOM PASSWORD
# ==================================================

def generate_password(

    tamanho=12
):

    caracteres = (

        string.ascii_letters

        + string.digits

        + "@#$%&*!"
    )

    return "".join(

        secrets.choice(caracteres)

        for _ in range(tamanho)
    )


# ==================================================
# LEGACY SHA256
# ==================================================

def legacy_sha256(password):

    password = sanitize_text(
        password
    )

    return hashlib.sha256(

        password.encode("utf-8")

    ).hexdigest()


# ==================================================
# PBKDF2 HASH
# ==================================================

def hash_password(password):

    password = sanitize_text(
        password
    )

    if not password:

        raise ValidationError(
            "Senha inválida."
        )

    salt = os.urandom(
        SALT_SIZE
    )

    dk = hashlib.pbkdf2_hmac(

        HASH_NAME,

        password.encode("utf-8"),

        salt,

        PBKDF2_ITERATIONS
    )

    salt_b64 = base64.b64encode(
        salt
    ).decode()

    hash_b64 = base64.b64encode(
        dk
    ).decode()

    return (

        f"{PASSWORD_PREFIX}$"

        f"{PBKDF2_ITERATIONS}$"

        f"{salt_b64}$"

        f"{hash_b64}"
    )


# ==================================================
# PASSWORD TYPE
# ==================================================

def is_pbkdf2_hash(hash_value):

    try:

        return str(hash_value).startswith(
            f"{PASSWORD_PREFIX}$"
        )

    except Exception:

        return False


def is_legacy_sha256(hash_value):

    try:

        hash_value = str(hash_value)

        return (

            len(hash_value)
            == LEGACY_SHA256_SIZE

            and

            all(

                c in string.hexdigits

                for c in hash_value
            )
        )

    except Exception:

        return False


# ==================================================
# PBKDF2 VERIFY
# ==================================================

def verify_pbkdf2(

    password,

    stored_hash
):

    try:

        password = sanitize_text(
            password
        )

        parts = stored_hash.split("$")

        if len(parts) != 4:

            return False

        prefix = parts[0]

        iterations = int(parts[1])

        salt = base64.b64decode(
            parts[2]
        )

        original_hash = (
            base64.b64decode(
                parts[3]
            )
        )

        if prefix != PASSWORD_PREFIX:

            return False

        new_hash = hashlib.pbkdf2_hmac(

            HASH_NAME,

            password.encode("utf-8"),

            salt,

            iterations
        )

        return hmac.compare_digest(

            new_hash,

            original_hash
        )

    except Exception:

        logger.exception(
            "VERIFY PBKDF2 ERROR"
        )

        return False


# ==================================================
# VERIFY PASSWORD
# ==================================================

def verify_password(

    password,

    stored_hash
):

    password = sanitize_text(
        password
    )

    stored_hash = sanitize_text(
        stored_hash
    )

    if (
        not password
        or
        not stored_hash
    ):

        return {

            "valido": False,

            "upgrade": False
        }

    # ==============================================
    # PBKDF2
    # ==============================================

    if is_pbkdf2_hash(
        stored_hash
    ):

        valido = verify_pbkdf2(

            password,

            stored_hash
        )

        return {

            "valido": valido,

            "upgrade": False
        }

    # ==============================================
    # LEGACY
    # ==============================================

    if is_legacy_sha256(
        stored_hash
    ):

        novo_hash = legacy_sha256(
            password
        )

        valido = hmac.compare_digest(

            novo_hash,

            stored_hash
        )

        return {

            "valido": valido,

            "upgrade": valido
        }

    return {

        "valido": False,

        "upgrade": False
    }


# ==================================================
# VALIDATE PASSWORD
# ==================================================

def validate_password_strength(

    password,

    minimo=6
):

    password = sanitize_text(
        password
    )

    if len(password) < minimo:

        raise ValidationError(

            (
                f"Senha deve possuir "
                f"mínimo de {minimo} caracteres."
            )
        )

    return True


# ==================================================
# SAFE COMPARE
# ==================================================

def safe_compare(

    valor1,

    valor2
):

    valor1 = sanitize_text(
        valor1
    )

    valor2 = sanitize_text(
        valor2
    )

    return hmac.compare_digest(
        valor1,
        valor2
    )


# ==================================================
# SANITIZE PAYLOAD
# ==================================================

def sanitize_payload(payload):

    if payload is None:
        return None

    secretos = {

        "senha",

        "password",

        "pwd",

        "token",

        "secret",

        "hash"
    }

    # ==============================================
    # DICT
    # ==============================================

    if isinstance(
        payload,
        dict
    ):

        resultado = {}

        for k, v in payload.items():

            chave = str(k).lower()

            if chave in secretos:

                resultado[k] = (
                    "[PROTEGIDO]"
                )

            else:

                resultado[k] = (
                    sanitize_payload(v)
                )

        return resultado

    # ==============================================
    # LIST
    # ==============================================

    if isinstance(
        payload,
        list
    ):

        return [

            sanitize_payload(x)

            for x in payload
        ]

    # ==============================================
    # STRING
    # ==============================================

    if isinstance(
        payload,
        str
    ):

        return sanitize_text(
            payload
        )

    return payload


# ==================================================
# AUTH TOKEN
# ==================================================

def create_session_token():

    return generate_token(48)


# ==================================================
# PASSWORD MIGRATION
# ==================================================

def needs_password_upgrade(

    stored_hash
):

    return is_legacy_sha256(
        stored_hash
    )


# ==================================================
# AUTHENTICATE
# ==================================================

def authenticate_user(

    password,

    stored_hash
):

    resultado = verify_password(

        password,

        stored_hash
    )

    if not resultado["valido"]:

        raise AuthenticationError(
            "Usuário ou senha inválidos."
        )

    return resultado