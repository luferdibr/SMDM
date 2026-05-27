from services.documento_service import (
    somente_digitos,
    validar_cnpj,
    validar_cpf,
)


def limpar_termo(valor):

    return str(
        valor or ""
    ).strip()


def tem_mascara_documento(valor):

    texto = limpar_termo(
        valor
    )

    return any(
        caractere in texto
        for caractere in (".", "-", "/")
    )


def classificar_termo_pesquisa(valor):

    texto = limpar_termo(
        valor
    )

    digitos = somente_digitos(
        texto
    )

    if not texto:
        return {
            "tipo": "vazio",
            "valor": "",
            "valido": True,
            "erro": "",
        }

    if digitos and len(digitos) == len(texto):
        if len(digitos) == 14:
            return {
                "tipo": "cnpj",
                "valor": digitos,
                "valido": validar_cnpj(digitos),
                "erro": "" if validar_cnpj(digitos) else "CNPJ invalido.",
            }

        if len(digitos) == 11 and validar_cpf(digitos):
            return {
                "tipo": "cpf",
                "valor": digitos,
                "valido": True,
                "erro": "",
            }

        return {
            "tipo": "telefone",
            "valor": digitos,
            "valido": True,
            "erro": "",
        }

    if digitos and tem_mascara_documento(texto):
        if len(digitos) == 11:
            valido = validar_cpf(digitos)
            return {
                "tipo": "cpf",
                "valor": digitos,
                "valido": valido,
                "erro": "" if valido else "CPF invalido.",
            }

        if len(digitos) == 14:
            valido = validar_cnpj(digitos)
            return {
                "tipo": "cnpj",
                "valor": digitos,
                "valido": valido,
                "erro": "" if valido else "CNPJ invalido.",
            }

    if digitos and not texto.replace(" ", "").isalpha():
        return {
            "tipo": "telefone",
            "valor": digitos,
            "valido": True,
            "erro": "",
        }

    return {
        "tipo": "nome",
        "valor": texto,
        "valido": True,
        "erro": "",
    }
