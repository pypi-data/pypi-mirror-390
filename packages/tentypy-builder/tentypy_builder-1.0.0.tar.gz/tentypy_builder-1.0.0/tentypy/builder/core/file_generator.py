"""
TentyPy Builder - File Generator
Author: Keniding
Description: Generador de archivos y directorios
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .template_engine import ProjectTemplate


class FileGenerator:
    """Generador de estructura de archivos"""

    def __init__(self, output_dir: Path):
        """
        Inicializar generador

        Args:
            output_dir: Directorio base donde generar el proyecto
        """
        self.output_dir = Path(output_dir)

    def generate_project(
        self,
        template: ProjectTemplate,
        project_name: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Generar proyecto completo desde plantilla

        Args:
            template: Plantilla del proyecto
            project_name: Nombre del proyecto
            variables: Variables personalizadas del usuario
        """
        project_path = self.output_dir / project_name

        if project_path.exists():
            raise FileExistsError(f"Project directory already exists: {project_path}")

        # Crear directorio raiz
        project_path.mkdir(parents=True, exist_ok=True)

        # Preparar variables
        all_variables = {
            **template.variables,
            **(variables or {}),
            "PROJECT_NAME": project_name,
            "AUTHOR": template.author,
        }

        # Generar estructura de directorios
        self._generate_structure(project_path, template.structure, all_variables)

        # Generar archivos con contenido
        self._generate_files(project_path, template.files, all_variables)

        print(f"Project '{project_name}' created successfully at {project_path}")

    def _generate_structure(
        self, base_path: Path, structure: List[Any], variables: Dict[str, str]
    ) -> None:
        """
        Generar estructura de directorios recursivamente

        Args:
            base_path: Ruta base
            structure: Lista de directorios/archivos
            variables: Variables para reemplazo
        """
        for item in structure:
            if isinstance(item, str):
                # Es un directorio o archivo simple
                item_path = base_path / self._replace_vars(item, variables)

                if item.endswith("/"):
                    # Es un directorio
                    item_path.mkdir(parents=True, exist_ok=True)
                else:
                    # Es un archivo vacio
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    item_path.touch()

            elif isinstance(item, dict):
                # Es un directorio con contenido
                for dir_name, contents in item.items():
                    dir_path = base_path / self._replace_vars(dir_name, variables)
                    dir_path.mkdir(parents=True, exist_ok=True)

                    if contents:
                        self._generate_structure(dir_path, contents, variables)

    def _generate_files(
        self, base_path: Path, files: Dict[str, str], variables: Dict[str, str]
    ) -> None:
        """
        Generar archivos con contenido

        Args:
            base_path: Ruta base del proyecto
            files: Diccionario {ruta: contenido}
            variables: Variables para reemplazo
        """
        for file_path, content in files.items():
            full_path = base_path / self._replace_vars(file_path, variables)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            processed_content = self._replace_vars(content, variables)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(processed_content)

    def _replace_vars(self, text: str, variables: Dict[str, str]) -> str:
        """
        Reemplazar variables en texto

        Args:
            text: Texto con variables {{VAR}}
            variables: Diccionario de variables

        Returns:
            Texto con variables reemplazadas
        """
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result
