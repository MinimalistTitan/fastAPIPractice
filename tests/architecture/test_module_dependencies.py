import ast
from pathlib import Path

MODULES_ROOT = Path(__file__).parents[2] / "src" / "app" / "modules"
INWARD_LAYERS = {
    "domain": {"application", "api", "infrastructure"},
    "application": {"api", "infrastructure"},
}


def imported_modules(tree: ast.AST) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    return imports


def test_business_module_dependency_direction() -> None:
    violations: list[str] = []
    for source_file in MODULES_ROOT.rglob("*.py"):
        relative_parts = source_file.relative_to(MODULES_ROOT).parts
        if len(relative_parts) < 3:
            continue
        source_module, source_layer = relative_parts[:2]
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))

        for imported in imported_modules(tree):
            parts = imported.split(".")
            if len(parts) < 4 or parts[:2] != ["app", "modules"]:
                continue
            target_module, target_layer = parts[2:4]

            if target_module != source_module and target_layer != "contracts":
                violations.append(f"{source_file}: cross-module import {imported}")
            if target_module == source_module and target_layer in INWARD_LAYERS.get(
                source_layer, set()
            ):
                violations.append(f"{source_file}: outward import {imported}")

    assert not violations, "\n".join(violations)
