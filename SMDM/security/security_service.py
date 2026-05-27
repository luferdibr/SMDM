
import logging

from datetime import (
    datetime,
    timedelta
)


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_SECURITY"
)


# ==================================================
# CONFIG
# ==================================================

MAX_TENTATIVAS = 5

MAX_NIVEL_BLOQUEIO = 5

ROOT_LEVEL = 100

MINUTOS_BASE = 5


# ==================================================
# HELPERS
# ==================================================

def now():

    return datetime.now()


def is_root(usuario):

    return int(

        usuario.get(
            "admin_level",
            0
        )

    ) >= ROOT_LEVEL


# ==================================================
# STATUS
# ==================================================

def usuario_bloqueado(usuario):

    # ==============================================
    # ROOT NUNCA BLOQUEIA
    # ==============================================

    if is_root(usuario):

        return {

            "bloqueado": False,

            "motivo": None
        }

    # ==============================================
    # BLOQUEIO TOTAL
    # ==============================================

    if usuario.get(
        "bloqueio_total"
    ):

        return {

            "bloqueado": True,

            "motivo": (
                "Usuário bloqueado "
                "permanentemente."
            )
        }

    # ==============================================
    # BLOQUEIO TEMPORARIO
    # ==============================================

    bloqueado_ate = usuario.get(
        "bloqueado_ate"
    )

    if bloqueado_ate:

        if now() < bloqueado_ate:

            minutos = int(

                (
                    bloqueado_ate
                    -
                    now()
                ).total_seconds() / 60
            ) + 1

            return {

                "bloqueado": True,

                "motivo": (

                    f"Usuário bloqueado "
                    f"temporariamente. "

                    f"Tente novamente em "
                    f"{minutos} minuto(s)."
                )
            }

    return {

        "bloqueado": False,

        "motivo": None
    }


# ==================================================
# RESET
# ==================================================

def resetar_seguranca(

    cursor,

    usuario_id
):

    cursor.execute("""

        UPDATE Usuarios

        SET

            TentativasLogin = 0,

            Bloqueado = 0,

            BloqueadoAte = NULL,

            NivelBloqueio = 0

        WHERE Id = ?

    """, (usuario_id,))


# ==================================================
# FALHA LOGIN
# ==================================================

def registrar_falha_login(

    cursor,

    usuario
):

    # ==============================================
    # ROOT NUNCA BLOQUEIA
    # ==============================================

    if is_root(usuario):

        cursor.execute("""

            UPDATE Usuarios

            SET

                TentativasLogin =
                    ISNULL(
                        TentativasLogin,
                        0
                    ) + 1

            WHERE Id = ?

        """, (

            usuario["id"],

        ))

        return {

            "bloqueado": False,

            "temporario": False,

            "total": False,

            "minutos": 0
        }

    # ==============================================
    # TENTATIVAS
    # ==============================================

    tentativas = int(

        usuario.get(
            "tentativas",
            0
        )

    ) + 1

    nivel = int(

        usuario.get(
            "nivel_bloqueio",
            0
        )

    )

    # ==============================================
    # AINDA NÃO BLOQUEIA
    # ==============================================

    if tentativas < MAX_TENTATIVAS:

        cursor.execute("""

            UPDATE Usuarios

            SET

                TentativasLogin = ?

            WHERE Id = ?

        """, (

            tentativas,

            usuario["id"]
        ))

        return {

            "bloqueado": False,

            "temporario": False,

            "total": False,

            "minutos": 0
        }

    # ==============================================
    # NOVO NIVEL
    # ==============================================

    nivel += 1

    # ==============================================
    # BLOQUEIO TOTAL
    # ==============================================

    if nivel >= MAX_NIVEL_BLOQUEIO:

        cursor.execute("""

            UPDATE Usuarios

            SET

                TentativasLogin = ?,

                NivelBloqueio = ?,

                BloqueioTotal = 1,

                Bloqueado = 1

            WHERE Id = ?

        """, (

            tentativas,

            nivel,

            usuario["id"]
        ))

        return {

            "bloqueado": True,

            "temporario": False,

            "total": True,

            "minutos": 0
        }

    # ==============================================
    # BLOQUEIO TEMPORARIO
    # ==============================================

    minutos = (

        nivel
        *
        MINUTOS_BASE
    )

    bloqueado_ate = (

        now()
        +
        timedelta(
            minutes=minutos
        )
    )

    cursor.execute("""

        UPDATE Usuarios

        SET

            TentativasLogin = ?,

            NivelBloqueio = ?,

            Bloqueado = 1,

            BloqueadoAte = ?

        WHERE Id = ?

    """, (

        tentativas,

        nivel,

        bloqueado_ate,

        usuario["id"]
    ))

    return {

        "bloqueado": True,

        "temporario": True,

        "total": False,

        "minutos": minutos
    }


# ==================================================
# LOGIN SUCESSO
# ==================================================

def registrar_login_sucesso(

    cursor,

    usuario_id
):

    cursor.execute("""

        UPDATE Usuarios

        SET

            TentativasLogin = 0,

            Bloqueado = 0,

            BloqueadoAte = NULL,

            UltimoLogin = GETDATE()

        WHERE Id = ?

    """, (usuario_id,))
