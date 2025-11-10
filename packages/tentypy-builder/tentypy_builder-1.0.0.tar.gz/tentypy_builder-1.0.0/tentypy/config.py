"""TentyPy Builder - Configuration Module."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class BuilderConfig:
    """Configuration class for TentyPy Builder.

    Attributes:
        templates_dir: Directory containing project templates.
        output_dir: Output directory for generated projects.
        supported_formats: Supported template file formats.
        overwrite_existing: Whether to overwrite existing files.
        create_git_repo: Whether to initialize a git repository.
        verbose: Enable verbose output.
        default_author: Default author name.
        default_version: Default project version.
        default_python_version: Default Python version requirement.
    """

    templates_dir: Path = field(default_factory=lambda: Path(__file__).parent / "templates")
    output_dir: Path = field(default_factory=Path.cwd)
    supported_formats: List[str] = field(default_factory=lambda: ["json", "yaml", "yml"])
    overwrite_existing: bool = False
    create_git_repo: bool = False
    verbose: bool = False
    default_author: str = "Unknown"
    default_version: str = "1.0.0"
    default_python_version: str = "3.11"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuilderConfig":
        """Create BuilderConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            BuilderConfig instance.
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert BuilderConfig to dictionary.

        Returns:
            Configuration dictionary.
        """
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
