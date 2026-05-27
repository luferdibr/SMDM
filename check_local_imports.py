import ast
from pathlib import Path


ROOT = Path("SMDM").resolve()


def module_name(path):
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def module_path(name):
    file_path = ROOT / Path(*name.split(".")).with_suffix(".py")
    if file_path.exists():
        return file_path

    init_path = ROOT / Path(*name.split(".")) / "__init__.py"
    if init_path.exists():
        return init_path

    return None


def defined_names(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        tree = ast.parse(path.read_text(encoding="latin1"))

    names = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                names.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)

    return names


def resolve_import(current_module, node):
    if node.level == 0:
        return node.module

    parts = current_module.split(".")
    if module_path(current_module) and module_path(current_module).name != "__init__.py":
        parts = parts[:-1]

    base = parts[: max(len(parts) - node.level + 1, 0)]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(base)


def main():
    py_files = [
        path
        for path in ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    export_cache = {}
    problems = []

    for path in py_files:
        current = module_name(path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            tree = ast.parse(path.read_text(encoding="latin1"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            if not node.module and node.level == 0:
                continue

            target_module = resolve_import(current, node)
            if not target_module:
                continue

            target_path = module_path(target_module)
            if not target_path:
                continue

            exports = export_cache.setdefault(
                target_module,
                defined_names(target_path),
            )

            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name not in exports:
                    problems.append(
                        (
                            path.relative_to(Path.cwd()),
                            node.lineno,
                            target_module,
                            alias.name,
                            target_path.relative_to(Path.cwd()),
                        )
                    )

    for path, line, target_module, name, target_path in problems:
        print(
            f"{path}:{line}: {target_module} "
            f"nao exporta {name} ({target_path})"
        )

    print(f"TOTAL={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
