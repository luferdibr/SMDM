
import logging
import bcrypt
import hashlib

from datetime import (
    datetime,
    timedelta
)

from database.connection import (
    get_connection
)

from services.auditoria_service import (
    registrar_evento
)

from config.settings import (
    SECURITY
)


# ==================================================
# CONFIG
# ==================================================

MAX_TENTATIVAS = int(

    SECURITY.get(
        "max_login_attempts",
        5
    )
)

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

HASH_TYPES = (
    "$2a$",
    "$2b$",
    "$2y$"
)


# ==================================================
# HELPERS
# ==================================================

def normalizar_login(login):

    return str(
        login or ""
    ).strip().upper()


def normalizar_senha(senha):

    return str(
        senha or ""
    ).strip()


def is_root(usuario):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL
    )


def is_admin(usuario):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ADMIN_LEVEL
    )


def possui_nivel(

    usuario,

    nivel
):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= int(nivel)
    )


# ==================================================
# HASH
# ==================================================

def gerar_hash(senha):

    senha = normalizar_senha(
        senha
    )

    return bcrypt.hashpw(

        senha.encode("utf-8"),

        bcrypt.gensalt()

    ).decode("utf-8")


def validar_hash(

    senha,

    senha_hash
):

    senha = normalizar_senha(
        senha
    )

    senha_hash = str(
        senha_hash or ""
    ).strip()

    if not senha:
        return False, None

    if not senha_hash:
        return False, None

    # ==============================================
    # BCRYPT
    # ==============================================

    try:

        if senha_hash.startswith(
            HASH_TYPES
        ):

            ok = bcrypt.checkpw(

                senha.encode("utf-8"),

                senha_hash.encode("utf-8")
            )

            if ok:
                return True, "bcrypt"

    except Exception:

        logging.exception(
            "BCRYPT VALIDATION ERROR"
        )

    # ==============================================
    # SHA256 LEGADO
    # ==============================================

    try:

        sha256_hash = hashlib.sha256(

            senha.encode("utf-8")

        ).hexdigest().lower()

        if sha256_hash == senha_hash.lower():

            return True, "sha256"

    except Exception:

        logging.exception(
            "SHA256 VALIDATION ERROR"
        )

    return False, None


# ==================================================
# AUDITORIA
# ==================================================

def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        logging.exception(
            "AUDITORIA ERROR"
        )


# ==================================================
# LOGIN FAIL
# ==================================================

def retorno_falha(**kwargs):

    retorno = {

        "autenticado": False,

        "ativo": False,

        "perfil_ativo": False,

        "bloqueado": False,

        "senha_expirada": False,

        "trocar_senha": False,

        "is_root": False,

        "is_admin": False
    }

    retorno.update(kwargs)

    return retorno


# ==================================================
# MAP USER
# ==================================================

def map_usuario(row):

    return {

        "id": row[0],

        "login": row[1],

        "nome": row[2],

        "senha_hash": row[3],

        "perfil_id": row[4],

        "ativo": bool(row[5]),

        "bloqueado": bool(row[6]),

        "tentativas": int(row[7] or 0),

        "deve_trocar": bool(row[8]),

        "senha_temporaria": bool(row[9]),

        "data_troca": row[10],

        "ultimo_login": row[11],

        "senha_migrada": bool(row[12]),

        "perfil_nome": row[13],

        "validade_senha": row[14],

        "perfil_ativo": bool(row[15]),

        "admin_level": int(row[16] or 0),

        "perfil_sistema": bool(row[17])
    }


# ==================================================
# UPDATE HELPERS
# ==================================================

def resetar_tentativas(

    cursor,

    user_id
):

    cursor.execute("""

        UPDATE Usuarios

        SET
            TentativasLogin = 0

        WHERE Id = ?

    """, (user_id,))


def incrementar_tentativas(

    cursor,

    user_id,

    tentativas
):

    tentativas = int(
        tentativas or 0
    ) + 1

    bloqueado = int(
        tentativas >= MAX_TENTATIVAS
    )

    cursor.execute("""

        UPDATE Usuarios

        SET
            TentativasLogin = ?,
            Bloqueado = ?

        WHERE Id = ?

    """, (

        tentativas,

        bloqueado,

        user_id
    ))


def atualizar_ultimo_login(

    cursor,

    user_id
):

    cursor.execute("""

        UPDATE Usuarios

        SET
            DataUltimoLogin = GETDATE()

        WHERE Id = ?

    """, (user_id,))


def migrar_sha256(

    cursor,

    user_id,

    senha
):

    novo_hash = gerar_hash(
        senha
    )

    cursor.execute("""

        UPDATE Usuarios

        SET
            SenhaHash = ?,
            SenhaMigrada = 1,
            DataUltimaTrocaSenha =
                ISNULL(
                    DataUltimaTrocaSenha,
                    GETDATE()
                )

        WHERE Id = ?

    """, (

        novo_hash,

        user_id
    ))


# ==================================================
# EXPIRAÇÃO
# ==================================================

def senha_expirada(

    admin_level,

    validade_dias,

    data_troca
):

    # ROOT NÃO EXPIRA

    if int(admin_level) >= ROOT_LEVEL:
        return False

    # SEM VALIDADE

    if not validade_dias:
        return False

    # NUNCA TROCOU

    if not data_troca:
        return True

    try:

        limite = (

            data_troca

            + timedelta(
                days=int(validade_dias)
            )
        )

        return datetime.now() > limite

    except Exception:

        logging.exception(
            "PASSWORD EXPIRATION ERROR"
        )

        return False


# ==================================================
# VALIDAR ROOT
# ==================================================

def validar_root(user):

    if not is_root(user):
        return

    if user["perfil_id"] != 1:

        raise Exception(
            "ROOT deve usar PerfilId=1."
        )

    if not user["perfil_sistema"]:

        raise Exception(
            "ROOT inválido."
        )


# ==================================================
# AUTENTICAÇÃO
# ==================================================

def autenticar(

    login,

    senha
):

    login = normalizar_login(
        login
    )

    senha = normalizar_senha(
        senha
    )

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                u.Id,
                u.Login,
                u.Nome,
                u.SenhaHash,
                u.PerfilId,
                u.Ativo,
                u.Bloqueado,
                u.TentativasLogin,
                u.DeveTrocarSenha,
                u.SenhaTemporaria,
                u.DataUltimaTrocaSenha,
                u.DataUltimoLogin,
                u.SenhaMigrada,

                p.Nome,
                p.ValidadeSenhaDias,
                p.Ativo,
                p.AdminLevel,
                p.Sistema

            FROM Usuarios u

            INNER JOIN Perfis p
                ON p.Id = u.PerfilId

            WHERE UPPER(u.Login) = ?

        """, (login,))

        row = cursor.fetchone()

        # ==========================================
        # NÃO EXISTE
        # ==========================================

        if not row:

            auditoria_segura(

                login=login,

                acao="LOGIN_INVALIDO",

                entidade="Usuarios",

                detalhes="Usuário inexistente"
            )

            return retorno_falha()

        # ==========================================
        # MAP
        # ==========================================

        user = map_usuario(
            row
        )

        user_id = user["id"]

        # ==========================================
        # ROOT
        # ==========================================

        validar_root(user)

        # ==========================================
        # USUÁRIO INATIVO
        # ==========================================

        if not user["ativo"]:

            auditoria_segura(

                usuario_id=user_id,

                login=user["login"],

                acao="LOGIN_USUARIO_INATIVO",

                entidade="Usuarios",

                registro_id=user_id
            )

            return retorno_falha(
                ativo=False
            )

        # ==========================================
        # PERFIL INATIVO
        # ==========================================

        if not user["perfil_ativo"]:

            auditoria_segura(

                usuario_id=user_id,

                login=user["login"],

                acao="LOGIN_PERFIL_INATIVO",

                entidade="Perfis",

                registro_id=user["perfil_id"]
            )

            return retorno_falha(
                ativo=True,
                perfil_ativo=False
            )

        # ==========================================
        # BLOQUEADO
        # ==========================================

        if user["bloqueado"]:

            auditoria_segura(

                usuario_id=user_id,

                login=user["login"],

                acao="LOGIN_BLOQUEADO",

                entidade="Usuarios",

                registro_id=user_id
            )

            return retorno_falha(
                ativo=True,
                perfil_ativo=True,
                bloqueado=True
            )

        # ==========================================
        # SENHA
        # ==========================================

        senha_ok, metodo = validar_hash(

            senha,

            user["senha_hash"]
        )

        if not senha_ok:

            incrementar_tentativas(

                cursor,

                user_id,

                user["tentativas"]
            )

            conn.commit()

            auditoria_segura(

                usuario_id=user_id,

                login=user["login"],

                acao="LOGIN_INVALIDO",

                entidade="Usuarios",

                registro_id=user_id,

                detalhes="Senha inválida"
            )

            return retorno_falha(
                ativo=True,
                perfil_ativo=True
            )

        # ==========================================
        # RESET LOGIN
        # ==========================================

        resetar_tentativas(
            cursor,
            user_id
        )

        # ==========================================
        # MIGRAR HASH
        # ==========================================

        if metodo == "sha256":

            migrar_sha256(

                cursor,

                user_id,

                senha
            )

            auditoria_segura(

                usuario_id=user_id,

                login=user["login"],

                acao="MIGRACAO_HASH",

                entidade="Usuarios",

                registro_id=user_id,

                detalhes=(
                    "SHA256 migrado para bcrypt"
                )
            )

        # ==========================================
        # EXPIRAÇÃO
        # ==========================================

        expirada = senha_expirada(

            user["admin_level"],

            user["validade_senha"],

            user["data_troca"]
        )

        # ==========================================
        # LOGIN
        # ==========================================

        atualizar_ultimo_login(
            cursor,
            user_id
        )

        conn.commit()

        # ==========================================
        # AUDITORIA
        # ==========================================

        auditoria_segura(

            usuario_id=user_id,

            login=user["login"],

            acao="LOGIN_SUCESSO",

            entidade="Usuarios",

            registro_id=user_id,

            detalhes=(
                f"perfil={user['perfil_nome']};"
                f"level={user['admin_level']};"
                f"hash={metodo}"
            )
        )

        logging.info(
            "Login realizado: %s",
            user["login"]
        )

        # ==========================================
        # RETORNO
        # ==========================================

        return {

            "autenticado": True,

            "id": user["id"],

            "login": user["login"],

            "nome": user["nome"],

            "perfil_id": user["perfil_id"],

            "perfil_nome": user["perfil_nome"],

            "admin_level": user["admin_level"],

            "perfil_sistema": (
                user["perfil_sistema"]
            ),

            "ativo": user["ativo"],

            "perfil_ativo": (
                user["perfil_ativo"]
            ),

            "bloqueado": False,

            "ultimo_login": (
                user["ultimo_login"]
            ),

            "senha_migrada": (
                user["senha_migrada"]
            ),

            "trocar_senha": (

                user["deve_trocar"]

                or

                user["senha_temporaria"]
            ),

            "senha_expirada": expirada,

            "is_root": is_root(user),

            "is_admin": is_admin(user),

            "auth_method": metodo
        }

    except Exception:

        try:

            if conn:
                conn.rollback()

        except Exception:
            pass

        logging.exception(
            "AUTH ERROR"
        )

        auditoria_segura(

            login=login,

            acao="AUTH_ERROR",

            entidade="Usuarios"
        )

        return retorno_falha()

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass