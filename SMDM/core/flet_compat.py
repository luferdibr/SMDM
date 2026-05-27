"""Compatibilidade entre versoes do Flet usadas no projeto."""

from __future__ import annotations

import flet as ft


def _border_all(width=1, color=None):
    side = ft.BorderSide(width, color)
    return ft.Border(
        top=side,
        right=side,
        bottom=side,
        left=side,
    )


def _padding_all(value):
    return ft.Padding(value, value, value, value)


def _padding_only(left=0, top=0, right=0, bottom=0):
    return ft.Padding(left, top, right, bottom)


def _padding_symmetric(horizontal=0, vertical=0):
    return ft.Padding(horizontal, vertical, horizontal, vertical)


def _margin_all(value):
    return ft.Margin(value, value, value, value)


def _margin_only(left=0, top=0, right=0, bottom=0):
    return ft.Margin(left, top, right, bottom)


def _margin_symmetric(horizontal=0, vertical=0):
    return ft.Margin(horizontal, vertical, horizontal, vertical)


def aplicar_compatibilidade_flet():
    """Recria atalhos removidos em versoes recentes do Flet."""

    if hasattr(ft, "border") and not hasattr(ft.border, "all"):
        ft.border.all = _border_all

    if hasattr(ft, "padding"):
        if not hasattr(ft.padding, "all"):
            ft.padding.all = _padding_all
        if not hasattr(ft.padding, "only"):
            ft.padding.only = _padding_only
        if not hasattr(ft.padding, "symmetric"):
            ft.padding.symmetric = _padding_symmetric

    if hasattr(ft, "margin"):
        if not hasattr(ft.margin, "all"):
            ft.margin.all = _margin_all
        if not hasattr(ft.margin, "only"):
            ft.margin.only = _margin_only
        if not hasattr(ft.margin, "symmetric"):
            ft.margin.symmetric = _margin_symmetric
