# ui/components/validators.py

import re

# =========================================================
# REQUIRED
# =========================================================

def required(
    value,
):

    return bool(
        str(value or "").strip()
    )

# =========================================================
# MIN LENGTH
# =========================================================

def min_length(
    value,
    length,
):

    return (
        len(
            str(value or "")
        )
        >= length
    )

# =========================================================
# MAX LENGTH
# =========================================================

def max_length(
    value,
    length,
):

    return (
        len(
            str(value or "")
        )
        <= length
    )

# =========================================================
# EMAIL
# =========================================================

def validate_email(
    email,
):

    if not required(email):

        return False

    pattern = (
        r"^[\w\.-]+@"
        r"[\w\.-]+\.\w+$"
    )

    return bool(
        re.match(
            pattern,
            email,
        )
    )

# =========================================================
# NUMBER
# =========================================================

def validate_number(
    value,
):

    try:

        float(value)

        return True

    except Exception:

        return False

# =========================================================
# INTEGER
# =========================================================

def validate_integer(
    value,
):

    try:

        int(value)

        return True

    except Exception:

        return False

# =========================================================
# POSITIVE NUMBER
# =========================================================

def validate_positive(
    value,
):

    try:

        return (
            float(value) > 0
        )

    except Exception:

        return False

# =========================================================
# PASSWORD
# =========================================================

def validate_password(
    password,
    min_size=6,
):

    if not required(password):

        return False

    if len(password) < min_size:

        return False

    return True

# =========================================================
# CPF
# =========================================================

def validate_cpf(
    cpf,
):

    cpf = re.sub(
        r"\D",
        "",
        str(cpf or ""),
    )

    if len(cpf) != 11:

        return False

    if cpf == cpf[0] * 11:

        return False

    return True

# =========================================================
# CNPJ
# =========================================================

def validate_cnpj(
    cnpj,
):

    cnpj = re.sub(
        r"\D",
        "",
        str(cnpj or ""),
    )

    if len(cnpj) != 14:

        return False

    if cnpj == cnpj[0] * 14:

        return False

    return True

# =========================================================
# PHONE
# =========================================================

def validate_phone(
    phone,
):

    phone = re.sub(
        r"\D",
        "",
        str(phone or ""),
    )

    return (
        len(phone)
        >= 10
    )

# =========================================================
# URL
# =========================================================

def validate_url(
    url,
):

    if not required(url):

        return False

    pattern = (
        r"^(http|https)://"
    )

    return bool(
        re.match(
            pattern,
            url,
        )
    )

# =========================================================
# DATE YYYY-MM-DD
# =========================================================

def validate_date(
    value,
):

    pattern = (
        r"^\d{4}-\d{2}-\d{2}$"
    )

    return bool(
        re.match(
            pattern,
            str(value or ""),
        )
    )

# =========================================================
# FIELD REQUIRED
# =========================================================

def field_required(
    field,
    message="Campo obrigatório.",
):

    if not required(field.value):

        field.error_text = message

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD EMAIL
# =========================================================

def field_email(
    field,
    message="E-mail inválido.",
):

    if not validate_email(
        field.value
    ):

        field.error_text = message

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD NUMBER
# =========================================================

def field_number(
    field,
    message="Número inválido.",
):

    if not validate_number(
        field.value
    ):

        field.error_text = message

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD PASSWORD
# =========================================================

def field_password(
    field,
    min_size=6,
):

    if not validate_password(
        field.value,
        min_size,
    ):

        field.error_text = (
            f"Mínimo "
            f"{min_size} caracteres."
        )

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD CPF
# =========================================================

def field_cpf(
    field,
):

    if not validate_cpf(
        field.value
    ):

        field.error_text = (
            "CPF inválido."
        )

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD CNPJ
# =========================================================

def field_cnpj(
    field,
):

    if not validate_cnpj(
        field.value
    ):

        field.error_text = (
            "CNPJ inválido."
        )

        return False

    field.error_text = None

    return True

# =========================================================
# FIELD PHONE
# =========================================================

def field_phone(
    field,
):

    if not validate_phone(
        field.value
    ):

        field.error_text = (
            "Telefone inválido."
        )

        return False

    field.error_text = None

    return True

# =========================================================
# CLEAR ERRORS
# =========================================================

def clear_errors(
    fields,
):

    for field in fields:

        try:

            field.error_text = None

        except Exception:

            pass

# =========================================================
# VALIDATE FORM
# =========================================================

def validate_form(
    validations,
):

    resultado = True

    for validation in validations:

        if not validation():

            resultado = False

    return resultado
