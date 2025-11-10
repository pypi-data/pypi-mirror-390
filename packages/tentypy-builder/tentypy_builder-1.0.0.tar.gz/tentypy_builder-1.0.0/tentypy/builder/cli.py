"""
TentyPy Builder - Enhanced CLI with Rich
Author: Keniding
Description: Interfaz de linea de comandos con colores y selectores
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

from .core.file_generator import FileGenerator
from .core.template_engine import TemplateEngine
from .core.validator import TemplateValidator

console = Console()


class BuilderCLI:
    """Interfaz de linea de comandos mejorada para TentyPy Builder"""

    def __init__(self):
        self.engine = TemplateEngine()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Crear parser de argumentos"""
        parser = argparse.ArgumentParser(
            prog="tentypy-builder",
            description="TentyPy Builder - Professional Project Structure Generator",
            epilog="Created by Keniding (Tenty)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Comando: create
        create_parser = subparsers.add_parser("create", help="Create a new project from template")
        create_parser.add_argument("project_name", nargs="?", help="Name of the project to create")
        create_parser.add_argument("-t", "--template", help="Template name")
        create_parser.add_argument(
            "-o",
            "--output",
            default=".",
            help="Output directory (default: current directory)",
        )
        create_parser.add_argument("-c", "--custom", help="Path to custom template JSON/YAML file")
        create_parser.add_argument(
            "-v", "--var", action="append", help="Set variable (format: KEY=VALUE)"
        )
        create_parser.add_argument(
            "-i", "--interactive", action="store_true", help="Interactive mode with prompts"
        )

        # Comando: list
        subparsers.add_parser("list", help="List available templates")

        # Comando: validate
        validate_parser = subparsers.add_parser("validate", help="Validate a template file")
        validate_parser.add_argument("template_file", help="Path to template JSON/YAML file")

        # Comando: info
        info_parser = subparsers.add_parser("info", help="Show template information")
        info_parser.add_argument("template_name", nargs="?", help="Name of the template")

        return parser

    def run(self, args: Optional[list] = None) -> int:
        """Ejecutar CLI"""
        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self._show_welcome()
            self.parser.print_help()
            return 1

        try:
            if parsed_args.command == "create":
                return self._handle_create(parsed_args)
            elif parsed_args.command == "list":
                return self._handle_list()
            elif parsed_args.command == "validate":
                return self._handle_validate(parsed_args)
            elif parsed_args.command == "info":
                return self._handle_info(parsed_args)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            return 1

        return 0

    def _show_welcome(self):
        """Mostrar mensaje de bienvenida"""
        welcome_text = """
        [bold cyan]TentyPy Builder[/bold cyan] [dim]v1.0.0[/dim]
        [green]Professional Project Structure Generator[/green]

        Created by [bold]Keniding (Tenty)[/bold]
        """
        console.print(Panel(welcome_text, box=box.DOUBLE, border_style="cyan"))

    def _handle_create(self, args) -> int:
        """Manejar comando create con modo interactivo"""

        # Modo interactivo
        if args.interactive or not args.project_name:
            return self._interactive_create()

        # Modo directo
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task = progress.add_task(f"[cyan]Creating project: {args.project_name}...", total=None)

            # Cargar plantilla
            if args.custom:
                template = self.engine.load_custom_template(Path(args.custom))
            else:
                template_name = args.template or "clean_architecture"
                template = self.engine.load_template(template_name)

            # Parsear variables
            user_vars = {}
            if args.var:
                for var in args.var:
                    if "=" in var:
                        key, value = var.split("=", 1)
                        user_vars[key.strip()] = value.strip()

            # Generar proyecto
            generator = FileGenerator(Path(args.output))
            generator.generate_project(template, args.project_name, user_vars)

            progress.update(task, completed=True)

        # Mostrar resumen
        self._show_project_summary(args.project_name, template, Path(args.output))

        return 0

    def _interactive_create(self) -> int:
        """Modo interactivo para crear proyecto"""
        console.print("\n[bold cyan] Interactive Project Creator[/bold cyan]\n")

        # Seleccionar template
        templates = self.engine.list_templates()

        console.print("[bold]Available templates:[/bold]")
        for i, template_name in enumerate(templates, 1):
            try:
                template = self.engine.load_template(template_name)
                console.print(f"  [cyan]{i}.[/cyan] {template_name:25} - {template.description}")
            except Exception:
                console.print(
                    f"  [cyan]{i}.[/cyan] {template_name:25} - [dim](Error loading)[/dim]"
                )

        template_choice = Prompt.ask(
            "\n[bold]Select template[/bold]",
            choices=[str(i) for i in range(1, len(templates) + 1)],
            default="1",
        )

        selected_template = templates[int(template_choice) - 1]
        template = self.engine.load_template(selected_template)

        # Nombre del proyecto
        project_name = Prompt.ask("[bold]Project name[/bold]", default="my_project")

        # Variables personalizadas
        console.print("\n[bold]Template variables:[/bold]")
        user_vars = {}
        for key, default_value in template.variables.items():
            value = Prompt.ask(f"  {key}", default=str(default_value))
            user_vars[key] = value

        # Confirmar
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Template: [cyan]{template.name}[/cyan]")
        console.print(f"  Project:  [cyan]{project_name}[/cyan]")
        console.print("  Output:   [cyan]./[/cyan]")

        if not Confirm.ask("\n[bold]Create project?[/bold]", default=True):
            console.print("[yellow]Cancelled[/yellow]")
            return 1

        # Generar proyecto
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Generating project...", total=None)

            generator = FileGenerator(Path("."))
            generator.generate_project(template, project_name, user_vars)

            progress.update(task, completed=True)

        self._show_project_summary(project_name, template, Path("."))

        return 0

    def _show_project_summary(self, project_name: str, template, output_dir: Path):
        """Mostrar resumen del proyecto creado"""
        project_path = output_dir / project_name

        console.print("\n[bold green]✓ Project created successfully![/bold green]\n")

        # Panel con información
        info = (
            f"[bold]Project:[/bold] {project_name}\n"
            f"[bold]Template:[/bold] {template.name}\n"
            f"[bold]Location:[/bold] {project_path.absolute()}\n"
            f"[bold]Author:[/bold] {template.author}"
        )
        console.print(Panel(info, title="📦 Project Info", border_style="green"))

        # Árbol de archivos (primeros niveles)
        console.print("\n[bold]Project structure:[/bold]")
        self._show_tree(project_path, max_depth=2)

        # Siguiente pasos
        next_steps = (
            f"1. cd {project_name}\n"
            "2. python -m venv venv\n"
            "3. venv\\Scripts\\activate  [dim](Windows)[/dim] or "
            "source venv/bin/activate [dim](Linux/Mac)[/dim]\n"
            "4. pip install -r requirements.txt\n"
            "5. Start coding! 🎉"
        )
        console.print(Panel(next_steps, title="Next Steps", border_style="cyan"))

    def _show_tree(self, path: Path, max_depth: int = 2, current_depth: int = 0):
        """Mostrar árbol de directorios"""
        if current_depth == 0:
            tree = Tree(f"📁 [bold cyan]{path.name}[/bold cyan]")
        else:
            tree = Tree("")

        if current_depth >= max_depth:
            return tree

        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for item in items[:10]:  # Limitar a 10 items
                if item.name.startswith("."):
                    continue

                if item.is_dir():
                    branch = tree.add(f"📁 [cyan]{item.name}[/cyan]")
                    if current_depth < max_depth - 1:
                        sub_items = list(item.iterdir())[:5]
                        for sub_item in sub_items:
                            if sub_item.is_dir():
                                branch.add(f"📁 [dim]{sub_item.name}[/dim]")
                            else:
                                branch.add(f"📄 [dim]{sub_item.name}[/dim]")
                else:
                    tree.add(f"📄 {item.name}")

            if len(items) > 10:
                tree.add("[dim]...[/dim]")

        except PermissionError:
            tree.add("[red]Permission denied[/red]")

        console.print(tree)
        return tree

    def _handle_list(self) -> int:
        """Manejar comando list con tabla bonita"""
        templates = self.engine.list_templates()

        table = Table(
            title="Available Templates",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Version", justify="center", style="green")

        for template_name in templates:
            try:
                template = self.engine.load_template(template_name)
                table.add_row(template_name, template.description, template.version)
            except Exception:
                table.add_row(template_name, "[red]Error loading template[/red]", "[dim]N/A[/dim]")

        console.print()
        console.print(table)
        console.print()

        return 0

    def _handle_validate(self, args) -> int:
        """Manejar comando validate"""
        import json

        template_path = Path(args.template_file)

        if not template_path.exists():
            console.print(f"[red]✗ File not found:[/red] {template_path}")
            return 1

        console.print(f"\n[bold]Validating template:[/bold] {template_path.name}\n")

        try:
            # Cargar archivo
            ext = template_path.suffix.lower()
            with open(template_path, "r", encoding="utf-8") as f:
                if ext == ".json":
                    data = json.load(f)
                elif ext in [".yaml", ".yml"]:
                    import yaml

                    data = yaml.safe_load(f)
                else:
                    console.print("[red]✗ Unsupported file format[/red]")
                    return 1

            # Validar
            is_valid, errors = TemplateValidator.validate(data)

            if is_valid:
                console.print("[bold green]✓ Template is valid![/bold green]\n")

                # Mostrar información
                info_table = Table(box=box.SIMPLE)
                info_table.add_column("Field", style="cyan")
                info_table.add_column("Value", style="white")

                info_table.add_row("Name", data.get("name", "N/A"))
                info_table.add_row("Description", data.get("description", "N/A"))
                info_table.add_row("Version", data.get("version", "N/A"))
                info_table.add_row("Author", data.get("author", "N/A"))

                console.print(info_table)
                return 0
            else:
                console.print("[bold red]✗ Template validation failed:[/bold red]\n")
                for error in errors:
                    console.print(f"  [red]•[/red] {error}")
                console.print()
                return 1

        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            return 1

    def _handle_info(self, args) -> int:
        """Manejar comando info con formato mejorado"""

        # Modo interactivo si no se especifica template
        if not args.template_name:
            templates = self.engine.list_templates()
            console.print("\n[bold]Available templates:[/bold]")
            for i, name in enumerate(templates, 1):
                console.print(f"  [cyan]{i}.[/cyan] {name}")

            choice = Prompt.ask(
                "\n[bold]Select template[/bold]",
                choices=[str(i) for i in range(1, len(templates) + 1)],
            )
            template_name = templates[int(choice) - 1]
        else:
            template_name = args.template_name

        try:
            template = self.engine.load_template(template_name)

            # Panel principal
            info = (
                f"[bold cyan]{template.name}[/bold cyan]\n"
                f"[dim]{template.description}[/dim]\n\n"
                f"[bold]Version:[/bold] {template.version}\n"
                f"[bold]Author:[/bold]  {template.author}"
            )
            console.print(Panel(info, box=box.DOUBLE, border_style="cyan"))

            # Tabla de variables
            if template.variables:
                console.print("\n[bold]Template Variables:[/bold]")
                var_table = Table(box=box.SIMPLE, show_header=False)
                var_table.add_column("Variable", style="cyan", no_wrap=True)
                var_table.add_column("Default Value", style="green")

                for key, value in template.variables.items():
                    var_table.add_row(key, str(value))

                console.print(var_table)

            # Estructura
            console.print("\n[bold]Project Structure:[/bold]")
            console.print(f"  [dim]{len(template.structure)} directories/files[/dim]")
            console.print(f"  [dim]{len(template.files)} files with content[/dim]")

            console.print()
            return 0

        except FileNotFoundError:
            console.print(f"[red]✗ Template not found:[/red] {template_name}")
            return 1


def main():
    """Entry point para CLI"""
    cli = BuilderCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
