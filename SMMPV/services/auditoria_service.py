
import json
import logging
import socket
from datetime import datetime

from database.connection import get_connection


# ==================================================
# CONFIG
# ==================================================

MAX_LOGIN = 50

MAX_EVENTO = 100

MAX_MODULO = 100

MAX_ENTIDADE = 100

MAX_DETALHES = 4000

MAX_IP = 50

MAX_HOST = 120


EVENTOS_VALIDOS = {

    "LOGIN_SUCCESS",

    "LOGIN_FAIL",

    "LOGOUT",

    "PASSWORD_CHANGE",

    "USER_CREATE",

    "USER_UPDATE",

    "USER_DISABLE",

    "USER_ENABLE",

    "PROFILE_CREATE",

    "PROFILE_UPDATE",

    "PROFILE_DISABLE",

    "MENU_CREATE",

    "MENU_UPDATE",

    "MENU_DELETE",

    "PERMISSION_SAVE",

    "PERMISSION_COPY",

    "SYSTEM_BOOT",

    "SYSTEM_INSTALL",

    "SYSTEM_ERROR"
}


# ==================================================
# HOST
# ==================================================

try:

    HOSTNAME = socket.gethostname()

except Exception:

    HOSTNAME = "UNKNOWN"


# ==================================================
# HELPERS
# ==================================================

def ok(
    mensagem="OK",
    dados=None
):

    return {

        "sucesso": True,

        "mensagem": mensagem,

        "dados": dados
    }


def erro(
    mensagem,
    dados=None
):

    return {

        "sucesso": False,

        "mensagem": str(mensagem),

        "dados": dados
    }


# ==================================================
# NORMALIZAR TEXTO
# ==================================================

def normalizar_texto(

    valor,

    tamanho=None,

    upper=False
):

    if valor is None:

        return None

    try:

        valor = str(valor).strip()

    except Exception:

        try:

            valor = json.dumps(

                valor,

                ensure_ascii=False,

                default=str
            )

        except Exception:

            valor = "[OBJETO_INVALIDO]"

    # ==============================================
    # SANITIZAÇÃO
    # ==============================================

    termos_proibidos = [

        "password",

        "senha",

        "token",

        "secret",

        "connection string",

        "pwd=",

        "uid="
    ]

    valor_lower = valor.lower()

    for termo in termos_proibidos:

        if termo in valor_lower:

            valor = "[CONTEUDO_SENSIVEL]"

            break

    if upper:

        valor = valor.upper()

    if tamanho:

        valor = valor[:tamanho]

    return valor


# ==================================================
# NORMALIZAR INTEIRO
# ==================================================

def normalizar_inteiro(valor):

    if valor in (
        None,
        ""
    ):
        return None

    try:

        return int(valor)

    except Exception:

        return None


# ==================================================
# SERIALIZAR
# ==================================================

def serializar_detalhes(detalhes):

    if detalhes is None:

        return None

    if isinstance(

        detalhes,

        (
            str,
            int,
            float,
            bool
        )
    ):

        return normalizar_texto(

            detalhes,

            tamanho=MAX_DETALHES
        )

    try:

        texto = json.dumps(

            detalhes,

            ensure_ascii=False,

            default=str
        )

        return normalizar_texto(

            texto,

            tamanho=MAX_DETALHES
        )

    except Exception:

        return "[DETALHE_INVALIDO]"


# ==================================================
# REGISTRAR EVENTO
# ==================================================

def registrar_evento(

    usuario=None,

    evento=None,

    descricao=None,

    entidade=None,

    registro_id=None,

    modulo=None,

    nivel="INFO",

    ip=None
):
    """
    Auditoria resiliente.

    Nunca deve quebrar o sistema.
    Nunca deve gerar rollback operacional.
    """

    conn = None

    cursor = None

    try:

        # ==========================================
        # USUÁRIO
        # ==========================================

        usuario_id = None

        login = None

        if isinstance(usuario, dict):

            usuario_id = normalizar_inteiro(

                usuario.get("id")
            )

            login = normalizar_texto(

                usuario.get("login"),

                tamanho=MAX_LOGIN,

                upper=True
            )

        # ==========================================
        # NORMALIZAÇÃO
        # ==========================================

        evento = normalizar_texto(

            evento or "EVENTO",

            tamanho=MAX_EVENTO,

            upper=True
        )

        descricao = serializar_detalhes(
            descricao
        )

        entidade = normalizar_texto(

            entidade,

            tamanho=MAX_ENTIDADE
        )

        modulo = normalizar_texto(

            modulo,

            tamanho=MAX_MODULO
        )

        nivel = normalizar_texto(

            nivel or "INFO",

            tamanho=20,

            upper=True
        )

        ip = normalizar_texto(

            ip,

            tamanho=MAX_IP
        )

        registro_id = normalizar_inteiro(
            registro_id
        )

        host = normalizar_texto(

            HOSTNAME,

            tamanho=MAX_HOST
        )

        # ==========================================
        # EVENTO
        # ==========================================

        if evento not in EVENTOS_VALIDOS:

            evento = "SYSTEM_ERROR"

        # ==========================================
        # CONNECTION
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # INSERT
        # ==========================================

        cursor.execute("""

            INSERT INTO Auditoria
            (
                UsuarioID,
                LoginUsuario,
                Evento,
                NivelLog,
                Modulo,
                Entidade,
                RegistroID,
                IPOrigem,
                HostOrigem,
                Descricao,
                DataEvento
            )

            VALUES
            (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, GETDATE()
            )

        """, (

            usuario_id,

            login,

            evento,

            nivel,

            modulo,

            entidade,

            registro_id,

            ip,

            host,

            descricao
        ))

        conn.commit()

        logging.info(

            (
                f"AUDITORIA "
                f"{evento} "
                f"{login or 'SYSTEM'}"
            )
        )

        return ok(
            "Evento registrado."
        )

    except Exception as ex:

        # ==========================================
        # ROLLBACK
        # ==========================================

        try:

            if conn:
                conn.rollback()

        except Exception:
            pass

        # ==========================================
        # FAIL SAFE
        # ==========================================

        logging.exception(
            "AUDITORIA ERROR"
        )

        return erro(ex)

    finally:

        # ==========================================
        # CURSOR
        # ==========================================

        try:

            if cursor:
                cursor.close()

        except Exception:
            pass

        # ==========================================
        # CONNECTION
        # ==========================================

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# REGISTRAR ERRO
# ==================================================

def registrar_erro(

    erro_obj,

    usuario=None,

    modulo=None,

    entidade=None
):

    try:

        return registrar_evento(

            usuario=usuario,

            evento="SYSTEM_ERROR",

            descricao=str(erro_obj),

            entidade=entidade,

            modulo=modulo,

            nivel="ERROR"
        )

    except Exception:

        logging.exception(
            "REGISTER ERROR FAIL"
        )

        return erro(
            "Falha auditoria."
        )


# ==================================================
# LISTAR EVENTOS
# ==================================================

def listar_eventos(

    usuario=None,

    filtro=None,

    evento=None,

    data_inicio=None,

    data_fim=None,

    limite=200
):

    conn = None

    cursor = None

    try:

        limite = int(limite)

        if limite <= 0:
            limite = 200

        if limite > 1000:
            limite = 1000

        conn = get_connection()

        cursor = conn.cursor()

        sql = """

            SELECT TOP (?)

                Id,
                UsuarioID,
                LoginUsuario,
                Evento,
                NivelLog,
                Modulo,
                Entidade,
                RegistroID,
                IPOrigem,
                HostOrigem,
                Descricao,
                DataEvento

            FROM Auditoria

            WHERE 1=1

        """

        params = [limite]

        # ==========================================
        # EVENTO
        # ==========================================

        if evento:

            sql += """

                AND Evento = ?

            """

            params.append(
                str(evento).upper()
            )

        # ==========================================
        # FILTRO
        # ==========================================

        if filtro:

            sql += """

                AND
                (
                    LoginUsuario LIKE ?
                    OR Evento LIKE ?
                    OR Descricao LIKE ?
                )

            """

            busca = f"%{filtro}%"

            params.extend([
                busca,
                busca,
                busca
            ])

        # ==========================================
        # DATA INICIO
        # ==========================================

        if data_inicio:

            sql += """

                AND DataEvento >= ?

            """

            params.append(data_inicio)

        # ==========================================
        # DATA FIM
        # ==========================================

        if data_fim:

            sql += """

                AND DataEvento <= ?

            """

            params.append(data_fim)

        sql += """

            ORDER BY
                Id DESC

        """

        cursor.execute(
            sql,
            tuple(params)
        )

        rows = cursor.fetchall()

        dados = []

        for r in rows:

            dados.append({

                "id": r[0],

                "usuario_id": r[1],

                "login": r[2],

                "evento": r[3],

                "nivel": r[4],

                "modulo": r[5],

                "entidade": r[6],

                "registro_id": r[7],

                "ip": r[8],

                "host": r[9],

                "descricao": r[10],

                "data_evento": (
                    r[11].isoformat()
                    if r[11]
                    else None
                )
            })

        return ok(
            dados=dados
        )

    except Exception as ex:

        logging.exception(
            "AUDIT LIST ERROR"
        )

        return erro(ex)

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