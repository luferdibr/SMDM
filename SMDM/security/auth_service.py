# =========================================================
# security/auth_service.py
# =========================================================

import logging
import bcrypt

from database.connection import (
    get_connection,
)

from security.session_service import (
    iniciar_sessao,
)

from services.auditoria_service import (
    auditoria_login,
    auditoria_error,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "AUTH_SERVICE"
)

TENTATIVAS_POR_PAUSA = 3

MINUTOS_POR_NIVEL = 5

# =========================================================
# LOGIN ATTEMPTS
# =========================================================

def registrar_falha_login(
    cursor,
    usuario_id,
    tentativas_atual,
):

    tentativas = int(
        tentativas_atual or 0
    ) + 1

    if tentativas % TENTATIVAS_POR_PAUSA:

        cursor.execute(

            """

            UPDATE Usuarios

            SET TentativasLogin = ?

            WHERE Id = ?

            """,

            (
                tentativas,
                usuario_id,
            ),
        )

        return {

            "tentativas": tentativas,

            "pausa_minutos": 0,
        }

    nivel = int(
        tentativas / TENTATIVAS_POR_PAUSA
    )

    pausa_minutos = (
        nivel * MINUTOS_POR_NIVEL
    )

    cursor.execute(

        """

        UPDATE Usuarios

        SET
            TentativasLogin = ?,
            NivelBloqueio = ?,
            BloqueadoAte = DATEADD(MINUTE, ?, GETDATE())

        WHERE Id = ?

        """,

        (
            tentativas,
            nivel,
            pausa_minutos,
            usuario_id,
        ),
    )

    return {

        "tentativas": tentativas,

        "pausa_minutos": pausa_minutos,
    }

# =========================================================
# VERIFY PASSWORD
# =========================================================

def verificar_senha(

    senha_plana: str,

    senha_hash: str,
):

    try:

        return bcrypt.checkpw(

            senha_plana.encode(
                "utf-8"
            ),

            senha_hash.encode(
                "utf-8"
            ),
        )

    except Exception:

        LOGGER.exception(
            "Erro bcrypt."
        )

        return False

# =========================================================
# AUTH
# =========================================================

def autenticar_usuario(

    login: str,

    senha: str,
):

    conn = None

    cursor = None

    try:

        LOGGER.info(
            f"Autenticando: {login}"
        )

        conn = get_connection()

        cursor = conn.cursor()

        # =============================================
        # SQL
        # =============================================

        sql = """

        SELECT TOP 1

            u.Id,
            u.Login,
            u.Nome,
            u.SenhaHash,
            u.PerfilId,
            u.Ativo,
            p.Sistema,
            u.Bloqueado,
            p.Nome,
            p.AdminLevel,
            u.DeveTrocarSenha,
            u.SenhaTemporaria,
            ISNULL(u.TentativasLogin, 0),
            DATEDIFF(SECOND, GETDATE(), u.BloqueadoAte),
            ISNULL(p.ValidadeSenhaDias, 0),
            DATEDIFF(DAY, u.DataUltimaTrocaSenha, GETDATE())

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE u.Login = ?
        AND u.Ativo = 1
        AND p.Ativo = 1

        """

        cursor.execute(
            sql,
            (login,),
        )

        row = cursor.fetchone()

        if not row:

            LOGGER.warning(
                "Usuário inexistente."
            )

            return None

        senha_hash = row[3]

        segundos_pausa = int(
            row[13] or 0
        )

        is_root_login = (
            str(row[1] or "").strip().upper()
            == "ROOT"
        )

        validade_senha_dias = int(
            row[14] or 0
        )

        dias_ultima_troca = int(
            row[15] or 0
        )

        senha_expirada = (
            validade_senha_dias > 0
            and
            dias_ultima_troca >= validade_senha_dias
            and
            not is_root_login
        )

        if (
            segundos_pausa > 0
            and
            not is_root_login
        ):

            minutos = int(
                (segundos_pausa + 59) / 60
            )

            LOGGER.warning(
                "Login em pausa: %s minuto(s).",
                minutos,
            )

            return None

        if row[7]:

            LOGGER.warning(
                "Usuário bloqueado."
            )

            return None

        # =============================================
        # VERIFY HASH
        # =============================================

        if not verificar_senha(

            senha,

            senha_hash,
        ):

            if is_root_login:

                LOGGER.warning(
                    "Senha ROOT inválida."
                )

            else:

                falha = registrar_falha_login(
                    cursor,
                    row[0],
                    row[12],
                )

                conn.commit()

                LOGGER.warning(
                    (
                        "Senha inválida. "
                        "Tentativas=%s Pausa=%s"
                    ),
                    falha["tentativas"],
                    falha["pausa_minutos"],
                )

            return None

        usuario = {

            "id": row[0],

            "login": row[1],

            "nome": row[2],

            "perfil_id": row[4],

            "ativo": row[5],

            "sistema": row[6],

            "perfil_nome": row[8],

            "admin": int(row[9] or 0) > 0,

            "admin_level": int(row[9] or 0),

            "deve_trocar": bool(row[10]),

            "trocar_senha": bool(row[10]),

            "senha_temporaria": bool(row[11]),

            "senha_expirada": senha_expirada,
        }

        cursor.execute(

            """

            UPDATE Usuarios

            SET
                UltimoLogin = GETDATE(),
                TentativasLogin = 0,
                NivelBloqueio = 0,
                BloqueadoAte = NULL

            WHERE Id = ?

            """,

            (row[0],),
        )

        conn.commit()

        # =============================================
        # SESSION
        # =============================================

        iniciar_sessao(
            usuario
        )

        # =============================================
        # AUDITORIA
        # =============================================

        try:

            auditoria_login(
                login
            )

        except Exception:

            LOGGER.exception(
                "Erro auditoria login."
            )

        LOGGER.info(
            f"Login OK: {login}"
        )

        return usuario

    except Exception as ex:

        LOGGER.exception(
            "Erro autenticação."
        )

        try:

            auditoria_error(

                "Erro autenticação",

                ex,
            )

        except Exception:

            pass

        return None

    finally:

        try:

            if cursor:

                cursor.close()

        except Exception:

            pass

        try:

            if conn:

                conn.close()

        except Exception:

            pass
