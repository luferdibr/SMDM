import re


def somente_digitos(valor):

    return re.sub(
        r"\D",
        "",
        str(valor or ""),
    )


def documento_vazio_ou_zerado(documento):

    return (
        not documento
        or set(documento) == {"0"}
    )


def validar_cpf(cpf):

    cpf = somente_digitos(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[i]) * (10 - i)
        for i in range(9)
    )
    digito = (soma * 10) % 11
    if digito == 10:
        digito = 0

    if digito != int(cpf[9]):
        return False

    soma = sum(
        int(cpf[i]) * (11 - i)
        for i in range(10)
    )
    digito = (soma * 10) % 11
    if digito == 10:
        digito = 0

    return digito == int(cpf[10])


def validar_cnpj(cnpj):

    cnpj = somente_digitos(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, *pesos_1]

    soma = sum(
        int(cnpj[i]) * pesos_1[i]
        for i in range(12)
    )
    resto = soma % 11
    digito = 0 if resto < 2 else 11 - resto

    if digito != int(cnpj[12]):
        return False

    soma = sum(
        int(cnpj[i]) * pesos_2[i]
        for i in range(13)
    )
    resto = soma % 11
    digito = 0 if resto < 2 else 11 - resto

    return digito == int(cnpj[13])


def normalizar_cpf(valor, campo="CPF", obrigatorio=False):

    documento = somente_digitos(valor)

    if documento_vazio_ou_zerado(documento):
        if obrigatorio:
            raise Exception(
                f"{campo} obrigatorio."
            )
        return ""

    if not validar_cpf(documento):
        raise Exception(
            f"{campo} invalido."
        )

    return documento


def normalizar_cnpj(valor, campo="CNPJ", obrigatorio=False):

    documento = somente_digitos(valor)

    if documento_vazio_ou_zerado(documento):
        if obrigatorio:
            raise Exception(
                f"{campo} obrigatorio."
            )
        return ""

    if not validar_cnpj(documento):
        raise Exception(
            f"{campo} invalido."
        )

    return documento


def normalizar_documento(
    valor,
    campo="Documento",
    obrigatorio=False,
    aceitar_cpf=True,
    aceitar_cnpj=True,
):

    documento = somente_digitos(valor)

    if documento_vazio_ou_zerado(documento):
        if obrigatorio:
            raise Exception(
                f"{campo} obrigatorio."
            )
        return ""

    if len(documento) == 11 and aceitar_cpf:
        if validar_cpf(documento):
            return documento
        raise Exception(
            f"{campo} CPF invalido."
        )

    if len(documento) == 14 and aceitar_cnpj:
        if validar_cnpj(documento):
            return documento
        raise Exception(
            f"{campo} CNPJ invalido."
        )

    tipos = []
    if aceitar_cpf:
        tipos.append("CPF")
    if aceitar_cnpj:
        tipos.append("CNPJ")

    raise Exception(
        f"{campo} deve ser {' ou '.join(tipos)} valido."
    )


def sql_documento_normalizado(coluna):

    return (
        f"REPLACE(REPLACE(REPLACE(REPLACE({coluna}, '.', ''), "
        f"'-', ''), '/', ''), ' ', '')"
    )
