from database.connection import get_connection


def _tem_texto(valor):

    return bool(str(valor or "").strip())


def _tem_coordenadas(latitude, longitude):

    return latitude is not None and longitude is not None


def validar_localizacao_para_orcamento(local_id, sede_id=None):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Endereco,
                Latitude,
                Longitude
            FROM LocalEvento
            WHERE LocalEventoID = ?
        """, (
            local_id,
        ))

        local = cursor.fetchone()

        if not local:
            raise Exception("Local do evento não encontrado.")

        if not _tem_texto(local[0]):
            raise Exception("Local do evento sem endereço. Não é possível gerar orçamento.")

        if not _tem_coordenadas(local[1], local[2]):
            raise Exception("Local do evento sem geolocalização. Não é possível calcular distância.")

        if sede_id:
            cursor.execute("""
                SELECT
                    Endereco,
                    Latitude,
                    Longitude
                FROM SedesEmpresa
                WHERE SedeID = ?
            """, (
                sede_id,
            ))
        else:
            cursor.execute("""
                SELECT TOP 1
                    Endereco,
                    Latitude,
                    Longitude
                FROM SedesEmpresa
                WHERE Ativo = 1
                AND Operacional = 1
                ORDER BY Fantasma, NomeSede
            """)

        sede = cursor.fetchone()

        if not sede:
            raise Exception("Nenhuma sede operacional encontrada para cálculo do orçamento.")

        if not _tem_texto(sede[0]):
            raise Exception("Sede sem endereço. Não é possível gerar orçamento.")

        if not _tem_coordenadas(sede[1], sede[2]):
            raise Exception("Sede sem geolocalização. Não é possível calcular distância.")

        return True

    finally:
        conn.close()
