"""
TentyPy Builder - Template Validator
Author: Keniding
Description: Validador de plantillas JSON
"""

from typing import Any, Dict, List, Tuple


class TemplateValidator:
    """Validador de plantillas de proyecto"""

    REQUIRED_FIELDS = ["name", "structure"]
    OPTIONAL_FIELDS = ["description", "version", "author", "files", "variables"]

    @staticmethod
    def validate(template_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validar estructura de plantilla

        Args:
            template_data: Datos de la plantilla

        Returns:
            Tupla (es_valido, lista_de_errores)
        """
        errors = []

        # Validar campos requeridos
        for field in TemplateValidator.REQUIRED_FIELDS:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")

        # Validar tipos
        if "name" in template_data and not isinstance(template_data["name"], str):
            errors.append("Field 'name' must be a string")

        if "structure" in template_data:
            if not isinstance(template_data["structure"], list):
                errors.append("Field 'structure' must be a list")
            else:
                struct_errors = TemplateValidator._validate_structure(template_data["structure"])
                errors.extend(struct_errors)

        if "files" in template_data and not isinstance(template_data["files"], dict):
            errors.append("Field 'files' must be a dictionary")

        if "variables" in template_data and not isinstance(template_data["variables"], dict):
            errors.append("Field 'variables' must be a dictionary")

        return len(errors) == 0, errors

    @staticmethod
    def _validate_structure(structure: List[Any], path: str = "") -> List[str]:
        """
        Validar estructura recursivamente

        Args:
            structure: Lista de estructura
            path: Ruta actual (para mensajes de error)

        Returns:
            Lista de errores encontrados
        """
        errors = []

        for i, item in enumerate(structure):
            current_path = f"{path}[{i}]"

            if isinstance(item, str):
                # Validacion basica de string
                if not item.strip():
                    errors.append(f"Empty string at {current_path}")

            elif isinstance(item, dict):
                # Validar diccionario
                for key, value in item.items():
                    if not isinstance(key, str):
                        errors.append(f"Dictionary key must be string at {current_path}")

                    if value is not None and not isinstance(value, list):
                        errors.append(
                            f"Dictionary value must be list or null at {current_path}.{key}"
                        )
                    elif isinstance(value, list):
                        nested_errors = TemplateValidator._validate_structure(
                            value, f"{current_path}.{key}"
                        )
                        errors.extend(nested_errors)
            else:
                errors.append(f"Invalid item type at {current_path}: must be string or dict")

        return errors
