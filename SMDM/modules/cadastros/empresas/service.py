from datetime import datetime

from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)


COLUNAS = [
    "RazaoSocial",
    "NomeFantasia",
    "TipoPessoa",
    "Documento",
    "InscricaoEstadual",
    "InscricaoMunicipal",
    "Inscricao",
    "DataFundacao",
    "AtividadeEconomica",
    "QuantidadeFuncionarios",
    "CNAE1",
    "CNAE2",
    "CNAE3",
    "CEP",
    "Logradouro",
    "Numero",
    "Complemento",
    "Bairro",
    "Municipio",
    "UF",
    "Pais",
    "Endereco",
    "Website",
    "Facebook",
    "Twitter",
    "Instagram",
    "Telefone1",
    "Telefone2",
    "Telefone3",
    "Responsavel1Cargo",
    "Responsavel1Nome",
    "Responsavel1Nacionalidade",
    "Responsavel1EstadoCivil",
    "Responsavel1Comerciante",
    "Responsavel1RG",
    "Responsavel1CPF",
    "Responsavel1DataNascimento",
    "Responsavel1Telefone",
    "Responsavel1Email",
    "Responsavel2Cargo",
    "Responsavel2Nome",
    "Responsavel2Nacionalidade",
    "Responsavel2EstadoCivil",
    "Responsavel2Comerciante",
    "Responsavel2RG",
    "Responsavel2CPF",
    "Responsavel2DataNascimento",
    "Responsavel2Telefone",
    "Responsavel2Email",
    "Responsavel3Cargo",
    "Responsavel3Nome",
    "Responsavel3Nacionalidade",
    "Responsavel3EstadoCivil",
    "Responsavel3Comerciante",
    "Responsavel3RG",
    "Responsavel3CPF",
    "Responsavel3DataNascimento",
    "Responsavel3Telefone",
    "Responsavel3Email",
    "ContatoNome",
    "ContatoDepartamento",
    "ContatoCargo",
    "ContatoTelefoneFixo",
    "ContatoCelular",
    "ContatoEmail",
    "QuemIndicou",
    "PrimeiroCanalContato",
    "Observacoes",
    "Ativo",
]


def limpar_texto(valor):

    return str(
        valor or ""
    ).strip()


def normalizar_data(valor, campo):

    valor = limpar_texto(
        valor
    )

    if not valor:
        return None

    for formato in (
        "%d/%m/%Y",
        "%Y-%m-%d",
    ):

        try:
            return datetime.strptime(
                valor,
                formato,
            ).date()
        except ValueError:
            pass

    raise Exception(
        f"{campo} inválida. Use DD/MM/AAAA."
    )


def normalizar_int(valor):

    valor = limpar_texto(
        valor
    )

    if not valor:
        return None

    try:
        return int(valor)
    except ValueError:
        raise Exception(
            "Quantidade de funcionários inválida."
        )


def normalizar_bool(valor):

    if isinstance(valor, bool):
        return int(valor)

    if valor is None:
        return 0

    return int(
        str(valor).strip().lower() in (
            "1",
            "true",
            "yes",
            "sim",
            "on",
        )
    )


def montar_endereco(dados):

    endereco = limpar_texto(
        dados.get("Endereco")
    )

    if endereco:
        return endereco

    partes = [
        dados.get("Logradouro"),
        dados.get("Numero"),
        dados.get("Complemento"),
        dados.get("Bairro"),
        dados.get("Municipio"),
        dados.get("UF"),
        dados.get("CEP"),
    ]

    return ", ".join(
        limpar_texto(parte)
        for parte in partes
        if limpar_texto(parte)
    )


def normalizar_dados(dados):

    razao_social = limpar_texto(
        dados.get("razao_social")
    )

    if not razao_social:
        raise Exception(
            "Informe a razão social."
        )

    normalizado = {
        "RazaoSocial": razao_social,
        "NomeFantasia": limpar_texto(dados.get("nome_fantasia")),
        "TipoPessoa": limpar_texto(dados.get("tipo_pessoa")),
        "Documento": limpar_texto(dados.get("documento")),
        "InscricaoEstadual": limpar_texto(dados.get("inscricao_estadual")),
        "InscricaoMunicipal": limpar_texto(dados.get("inscricao_municipal")),
        "Inscricao": limpar_texto(dados.get("inscricao")),
        "DataFundacao": normalizar_data(dados.get("data_fundacao"), "Data da fundação"),
        "AtividadeEconomica": limpar_texto(dados.get("atividade_economica")),
        "QuantidadeFuncionarios": normalizar_int(dados.get("quantidade_funcionarios")),
        "CNAE1": limpar_texto(dados.get("cnae1")),
        "CNAE2": limpar_texto(dados.get("cnae2")),
        "CNAE3": limpar_texto(dados.get("cnae3")),
        "CEP": limpar_texto(dados.get("cep")),
        "Logradouro": limpar_texto(dados.get("logradouro")),
        "Numero": limpar_texto(dados.get("numero")),
        "Complemento": limpar_texto(dados.get("complemento")),
        "Bairro": limpar_texto(dados.get("bairro")),
        "Municipio": limpar_texto(dados.get("municipio") or dados.get("cidade")),
        "UF": limpar_texto(dados.get("uf") or dados.get("estado")).upper(),
        "Pais": limpar_texto(dados.get("pais")) or "Brasil",
        "Website": limpar_texto(dados.get("website")),
        "Facebook": limpar_texto(dados.get("facebook")),
        "Twitter": limpar_texto(dados.get("twitter")),
        "Instagram": limpar_texto(dados.get("instagram")),
        "Telefone1": limpar_texto(dados.get("telefone1")),
        "Telefone2": limpar_texto(dados.get("telefone2")),
        "Telefone3": limpar_texto(dados.get("telefone3")),
        "ContatoNome": limpar_texto(dados.get("contato_nome")),
        "ContatoDepartamento": limpar_texto(dados.get("contato_departamento")),
        "ContatoCargo": limpar_texto(dados.get("contato_cargo")),
        "ContatoTelefoneFixo": limpar_texto(dados.get("contato_telefone_fixo")),
        "ContatoCelular": limpar_texto(dados.get("contato_celular")),
        "ContatoEmail": limpar_texto(dados.get("contato_email")),
        "QuemIndicou": limpar_texto(dados.get("quem_indicou")),
        "PrimeiroCanalContato": limpar_texto(dados.get("primeiro_canal")),
        "Observacoes": limpar_texto(dados.get("observacoes")),
        "Ativo": normalizar_bool(dados.get("ativo", True)),
    }

    for indice in (1, 2, 3):

        prefixo_db = f"Responsavel{indice}"
        prefixo_form = f"responsavel{indice}"

        normalizado[f"{prefixo_db}Cargo"] = limpar_texto(dados.get(f"{prefixo_form}_cargo"))
        normalizado[f"{prefixo_db}Nome"] = limpar_texto(dados.get(f"{prefixo_form}_nome"))
        normalizado[f"{prefixo_db}Nacionalidade"] = limpar_texto(dados.get(f"{prefixo_form}_nacionalidade"))
        normalizado[f"{prefixo_db}EstadoCivil"] = limpar_texto(dados.get(f"{prefixo_form}_estado_civil"))
        normalizado[f"{prefixo_db}Comerciante"] = normalizar_bool(dados.get(f"{prefixo_form}_comerciante"))
        normalizado[f"{prefixo_db}RG"] = limpar_texto(dados.get(f"{prefixo_form}_rg"))
        normalizado[f"{prefixo_db}CPF"] = limpar_texto(dados.get(f"{prefixo_form}_cpf"))
        normalizado[f"{prefixo_db}DataNascimento"] = normalizar_data(
            dados.get(f"{prefixo_form}_data_nascimento"),
            f"Data de nascimento do responsável {indice}",
        )
        normalizado[f"{prefixo_db}Telefone"] = limpar_texto(dados.get(f"{prefixo_form}_telefone"))
        normalizado[f"{prefixo_db}Email"] = limpar_texto(dados.get(f"{prefixo_form}_email"))

    normalizado["Endereco"] = montar_endereco(
        normalizado
    )

    return normalizado


def existe_documento(documento, empresa_id=None):

    documento = limpar_texto(
        documento
    )

    if not documento:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    if empresa_id:

        cursor.execute("""
            SELECT COUNT(*)
            FROM Empresa
            WHERE Documento = ?
            AND EmpresaID <> ?
        """, (
            documento,
            empresa_id,
        ))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM Empresa
            WHERE Documento = ?
        """, (
            documento,
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


def listar_empresas():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            EmpresaID,
            RazaoSocial,
            ISNULL(NomeFantasia, ''),
            ISNULL(Documento, ''),
            ISNULL(ContatoNome, ''),
            ISNULL(ContatoCelular, ''),
            ISNULL(ContatoEmail, ''),
            Ativo
        FROM Empresa
        ORDER BY RazaoSocial
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def obter_empresa(empresa_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            EmpresaID,
            {", ".join(COLUNAS)}
        FROM Empresa
        WHERE EmpresaID = ?
    """, (
        empresa_id,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


def salvar_empresa(empresa_id, dados):

    dados = normalizar_dados(
        dados
    )

    if existe_documento(
        dados["Documento"],
        empresa_id,
    ):

        raise Exception(
            "Já existe uma empresa cadastrada com esse CNPJ/CPF."
        )

    conn = get_connection()

    cursor = conn.cursor()

    valores = [
        dados.get(coluna)
        for coluna in COLUNAS
    ]

    try:

        if empresa_id:

            set_sql = ", ".join(
                f"{coluna} = ?"
                for coluna in COLUNAS
            )

            cursor.execute(f"""
                UPDATE Empresa
                SET
                    {set_sql},
                    AtualizadoEm = GETDATE()
                WHERE EmpresaID = ?
            """, (
                *valores,
                empresa_id,
            ))

        else:

            colunas_sql = ", ".join(
                COLUNAS
            )

            marcadores = ", ".join(
                "?"
                for _ in COLUNAS
            )

            if coluna_eh_identity(
                cursor,
                "Empresa",
                "EmpresaID",
            ):

                cursor.execute(f"""
                    INSERT INTO Empresa ({colunas_sql})
                    VALUES ({marcadores})
                """, valores)

            else:

                cursor.execute(f"""
                    INSERT INTO Empresa (EmpresaID, {colunas_sql})
                    VALUES (?, {marcadores})
                """, (
                    obter_proximo_id(
                        cursor,
                        "Empresa",
                        "EmpresaID",
                    ),
                    *valores,
                ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def excluir_empresa(empresa_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM Empresa
            WHERE EmpresaID = ?
        """, (
            empresa_id,
        ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()
