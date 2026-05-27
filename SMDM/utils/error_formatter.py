# =========================================================
# utils/error_formatter.py
# =========================================================

import traceback


def get_error_details(
    ex,
):

    tb = traceback.extract_tb(
        ex.__traceback__
    )

    frame = (
        tb[-1]
        if tb
        else None
    )

    error_type = type(ex).__name__

    details = {
        "tipo": error_type,
        "codigo": error_type,
        "mensagem": str(ex),
        "arquivo": "",
        "linha": "",
        "funcao": "",
        "codigo_linha": "",
        "traceback": "".join(
            traceback.format_exception(
                type(ex),
                ex,
                ex.__traceback__,
            )
        ),
    }

    if frame:

        details.update(
            {
                "arquivo": frame.filename,
                "linha": frame.lineno,
                "funcao": frame.name,
                "codigo_linha": (
                    frame.line
                    or ""
                ),
            }
        )

    return details


def format_error_message(
    ex,
    contexto=None,
    include_traceback=False,
):

    details = get_error_details(
        ex
    )

    lines = []

    if contexto:

        lines.append(
            f"Contexto: {contexto}"
        )

    lines.extend(
        [
            (
                "Erro: "
                f"{details['codigo']} - "
                f"{details['mensagem']}"
            ),
            (
                "Arquivo: "
                f"{details['arquivo']}"
            ),
            (
                "Linha: "
                f"{details['linha']}"
            ),
            (
                "Função: "
                f"{details['funcao']}"
            ),
            (
                "Código: "
                f"{details['codigo_linha']}"
            ),
        ]
    )

    if include_traceback:

        lines.extend(
            [
                "",
                "Traceback:",
                details["traceback"],
            ]
        )

    return "\n".join(lines)
