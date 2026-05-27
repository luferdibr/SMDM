import ast
from pathlib import Path


BUTTONS = {
    "ElevatedButton",
    "FilledButton",
    "OutlinedButton",
    "TextButton",
}


def is_flet_button(node):
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr not in BUTTONS:
        return False
    return (
        isinstance(node.func.value, ast.Name)
        and node.func.value.id == "ft"
    )


def main():
    root = Path("SMDM")
    total = 0

    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not is_flet_button(node):
                continue

            bad = [
                kw.arg
                for kw in node.keywords
                if kw.arg == "text"
            ]

            if bad:
                total += 1
                print(
                    f"{path}:{node.lineno}: "
                    f"ft.{node.func.attr} usa {', '.join(bad)}"
                )

    print(f"TOTAL={total}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
