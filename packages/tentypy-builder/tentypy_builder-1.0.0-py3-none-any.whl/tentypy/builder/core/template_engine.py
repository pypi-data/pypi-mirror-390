"""
TentyPy Builder - Template Engine with YAML Support
Author: Keniding
Description: Motor de plantillas con soporte JSON y YAML
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class FileTemplate:
    """Representa un archivo a generar"""

    path: str
    content: str
    is_directory: bool = False


@dataclass
class ProjectTemplate:
    """Representa una plantilla de proyecto completa"""

    name: str
    description: str
    version: str
    author: str
    structure: List[Dict[str, Any]]
    files: Dict[str, str]
    variables: Dict[str, str]


class TemplateEngine:
    """Motor para procesar plantillas de proyecto"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"

    def load_template(self, template_name: str) -> ProjectTemplate:
        """
        Cargar plantilla desde archivo JSON o YAML

        Args:
            template_name: Nombre de la plantilla (sin extension)

        Returns:
            ProjectTemplate con la configuracion cargada

        Raises:
            FileNotFoundError: Si la plantilla no existe
            ValueError: Si el formato es invalido
        """
        # Buscar archivo con cualquier extension soportada
        template_path = None
        for ext in [".json", ".yaml", ".yml"]:
            candidate = self.templates_dir / f"{template_name}{ext}"
            if candidate.exists():
                template_path = candidate
                break

        if template_path is None:
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")

        return self.load_custom_template(template_path)

    def load_custom_template(self, template_path: Path) -> ProjectTemplate:
        """
        Cargar plantilla desde ruta personalizada

        Args:
            template_path: Ruta al archivo JSON o YAML

        Returns:
            ProjectTemplate con la configuracion cargada
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Determinar formato por extension
        ext = template_path.suffix.lower()

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    data = json.load(f)
                elif ext in [".yaml", ".yml"]:
                    if not YAML_AVAILABLE:
                        raise ImportError(
                            "PyYAML is required for YAML support. "
                            "Install it with: pip install pyyaml"
                        )
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported template format: {ext}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid template format: {e}")

        return ProjectTemplate(
            name=data.get("name", template_path.stem),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            structure=data.get("structure", []),
            files=data.get("files", {}),
            variables=data.get("variables", {}),
        )

    def list_templates(self) -> List[str]:
        """
        Listar todas las plantillas disponibles

        Returns:
            Lista de nombres de plantillas
        """
        templates = set()
        for ext in ["*.json", "*.yaml", "*.yml"]:
            for f in self.templates_dir.glob(ext):
                templates.add(f.stem)
        return sorted(list(templates))

    def replace_variables(
        self, content: str, variables: Dict[str, str], user_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Reemplazar variables en el contenido

        Args:
            content: Contenido con variables {{VAR}}
            variables: Variables por defecto de la plantilla
            user_vars: Variables proporcionadas por el usuario

        Returns:
            Contenido con variables reemplazadas
        """
        all_vars = {**variables, **(user_vars or {})}

        result = content
        for key, value in all_vars.items():
            result = result.replace(f"{{{{{key}}}}}", value)

        return result
