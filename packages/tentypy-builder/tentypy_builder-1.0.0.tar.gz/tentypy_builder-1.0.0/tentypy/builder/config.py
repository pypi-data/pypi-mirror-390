"""
TentyPy Builder - Configuration
Author: Keniding
Description: Configuracion global del builder
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class BuilderConfig:
    """Configuracion del builder"""

    # Directorios
    templates_dir: Path = field(default_factory=lambda: Path(__file__).parent / "templates")
    output_dir: Path = field(default_factory=lambda: Path.cwd())

    # Formatos soportados
    supported_formats: List[str] = field(default_factory=lambda: ["json", "yaml", "yml"])

    # Configuracion de generacion
    overwrite_existing: bool = False
    create_git_repo: bool = False
    verbose: bool = False

    # Variables globales
    default_author: str = "Unknown"
    default_version: str = "1.0.0"
    default_python_version: str = "3.11"

    @classmethod
    def from_dict(cls, data: dict) -> "BuilderConfig":
        """Crear configuracion desde diccionario"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_dict(self) -> dict:
        """Convertir configuracion a diccionario"""
        return {
            "templates_dir": str(self.templates_dir),
            "output_dir": str(self.output_dir),
            "supported_formats": self.supported_formats,
            "overwrite_existing": self.overwrite_existing,
            "create_git_repo": self.create_git_repo,
            "verbose": self.verbose,
            "default_author": self.default_author,
            "default_version": self.default_version,
            "default_python_version": self.default_python_version,
        }


# Configuracion global por defecto
DEFAULT_CONFIG = BuilderConfig()
