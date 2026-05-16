
import logging
import re

import bcrypt


# ==================================================
# CONFIG
# ==================================================

BCRYPT_ROUNDS = 12

MIN_LENGTH = 8

REQUIRE_UPPER = True

REQUIRE_LOWER = True

REQUIRE_NUMBER = True

REQUIRE_SPECIAL = True


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_PASSWORD"
)


# ==================================================
# HELPERS
# ==================================================

def to_bytes(valor):

    if isinstance(valor, bytes):
        return valor

    return str(valor).encode("utf-8")


# ==================================================
# HASH
# ==================================================

def gerar_hash(senha):

    try:

        senha = str(
            senha or ""
        ).strip()

        if not senha:

            raise Exception(
                "Senha vazia."
            )

        senha_bytes = to_bytes(
            senha
        )

        salt = bcrypt.gensalt(
            rounds=BCRYPT_ROUNDS
        )

        senha_hash = bcrypt.hashpw(

            senha_bytes,

            salt
        )

        return senha_hash.decode(
            "utf-8"
        )

    except Exception:

        LOGGER.exception(
            "HASH ERROR"
        )

        raise


# ==================================================
# VERIFY
# ==================================================

def verificar_senha(

    senha,

    senha_hash
):

    try:

        senha = str(
            senha or ""
        ).strip()

        senha_hash = str(
            senha_hash or ""
        ).strip()

        if not senha:
            return False

        if not senha_hash:
            return False

        senha_bytes = to_bytes(
            senha
        )

        hash_bytes = to_bytes(
            senha_hash
        )

        return bcrypt.checkpw(

            senha_bytes,

            hash_bytes
        )

    except Exception:

        LOGGER.exception(
            "VERIFY PASSWORD ERROR"
        )

        return False


# ==================================================
# POLÍTICA
# ==================================================

def validar_politica_senha(
    senha
):

    erros = []

    senha = str(
        senha or ""
    )

    # ==============================================
    # LENGTH
    # ==============================================

    if len(senha) < MIN_LENGTH:

        erros.append(

            (
                f"Senha deve possuir "
                f"mínimo de "
                f"{MIN_LENGTH} caracteres."
            )
        )

    # ==============================================
    # UPPER
    # ==============================================

    if REQUIRE_UPPER:

        if not re.search(
            r"[A-Z]",
            senha
        ):

            erros.append(

                (
                    "Senha deve possuir "
                    "letra maiúscula."
                )
            )

    # ==============================================
    # LOWER
    # ==============================================

    if REQUIRE_LOWER:

        if not re.search(
            r"[a-z]",
            senha
        ):

            erros.append(

                (
                    "Senha deve possuir "
                    "letra minúscula."
                )
            )

    # ==============================================
    # NUMBER
    # ==============================================

    if REQUIRE_NUMBER:

        if not re.search(
            r"[0-9]",
            senha
        ):

            erros.append(

                (
                    "Senha deve possuir "
                    "número."
                )
            )

    # ==============================================
    # SPECIAL
    # ==============================================

    if REQUIRE_SPECIAL:

        if not re.search(
            r"[!@#$%¨&*()_+=\\-{}\\[\\]:;\"'<>,.?/\\\\|]",
            senha
        ):

            erros.append(

                (
                    "Senha deve possuir "
                    "caractere especial."
                )
            )

    return {

        "valida": len(erros) == 0,

        "erros": erros
    }


# ==================================================
# FORÇA
# ==================================================

def avaliar_forca_senha(
    senha
):

    senha = str(
        senha or ""
    )

    score = 0

    if len(senha) >= 8:
        score += 1

    if len(senha) >= 12:
        score += 1

    if re.search(r"[A-Z]", senha):
        score += 1

    if re.search(r"[a-z]", senha):
        score += 1

    if re.search(r"[0-9]", senha):
        score += 1

    if re.search(
        r"[!@#$%¨&*()_+=\\-{}\\[\\]:;\"'<>,.?/\\\\|]",
        senha
    ):
        score += 1

    # ==============================================
    # CLASSIFICAÇÃO
    # ==============================================

    if score <= 2:

        nivel = "FRACA"

    elif score <= 4:

        nivel = "MEDIA"

    else:

        nivel = "FORTE"

    return {

        "score": score,

        "nivel": nivel
    }


# ==================================================
# COMPAT
# ==================================================

def needs_rehash(senha_hash):

    try:

        senha_hash = str(
            senha_hash or ""
        )

        return not senha_hash.startswith(
            "$2"
        )

    except Exception:

        return True
