import typer
from pathlib import Path
from fapi.utils.ustils import render_template, ensure_fastapi_project

add = typer.Typer(help="Adds entities like models, schemas, routes...")

TEMPLATES_DIR = Path("fapi/templates")


@add.command()
def route(name: str):
    """Create a new route file"""
    ensure_fastapi_project()
    if not name:
        typer.echo("You must provide a name for the route")
        raise typer.Exit()

    project_path = Path(".")
    context = {"name": name.lower(), "class_name": name.capitalize()}

    routes_dir = project_path / "app/api/routes"
    routes_dir.mkdir(parents=True, exist_ok=True)

    render_template("app/api/routes/route.py.j2", routes_dir / f"{name.lower()}.py", context)

    typer.echo(f"✅ Route `{name}` created successfully!")


@add.command()
def model(
    name: str,
    schema: bool = typer.Option(False, "--schema", help="Add a schema file"),
    crud: bool = typer.Option(False, "--crud", help="Add a CRUD file")
):
    ensure_fastapi_project()
    if not name:
        typer.echo("You must provide a name for the model")
        raise typer.Exit()

    project_path = Path(".")
    context = {"name": name.lower(), "class_name": name.capitalize()}

    models_dir = project_path / "app/models"
    models_dir.mkdir(parents=True, exist_ok=True)

    render_template("app/models/model.py.j2", models_dir / f"{name.lower()}.py", context)

    if schema:
        schemas_dir = project_path / "app/schemas"
        schemas_dir.mkdir(parents=True, exist_ok=True)

        render_template("app/schemas/schema.py.j2", schemas_dir / f"{name.lower()}_schema.py", context)
        typer.echo(f"📦 Schema `{name}` created")

    if crud:
        crud_dir = project_path / "app/crud"
        crud_dir.mkdir(parents=True, exist_ok=True)

        render_template("app/crud/crud.py.j2", crud_dir / f"{name.lower()}_crud.py", context)
        typer.echo(f"🛠️ CRUD `{name}` created")

    typer.echo(f"✅ Model `{name}` created successfully!")


@add.command()
def service(name: str):
    """Create a new service file"""
    ensure_fastapi_project()

    if not name:
        typer.echo("You must provide a name for the service")
        raise typer.Exit()

    project_path = Path(".")
    context = {"name": name.lower(), "calss_name": name.capitalize()}

    routes_dir = project_path / "app/services"
    routes_dir.mkdir(parents=True, exist_ok=True)

    render_template("app/services/service.py.j2", routes_dir / f"{name.lower()}.py", context)

    typer.echo(f"✅ service `{name}` created successfully!")



@add.command()
def crud(name: str):
    """Create a new crud file"""

    ensure_fastapi_project()

    if not name:
        typer.echo("You must provide a name for the service")
        raise typer.Exit()

    project_path = Path(".")
    context = {"name": name.lower(), "calss_name": name.capitalize()}

    routes_dir = project_path / "app/crud"
    routes_dir.mkdir(parents=True, exist_ok=True)

    render_template("app/crud/crud.py.j2", routes_dir / f"{name.lower()}.py", context)

    typer.echo(f"✅ crud `{name}` created successfully!")

@add.command()
def schema(name: str):
    """Create a new schema file"""
    
    ensure_fastapi_project()

    if not name:
        typer.echo("You must provide a name for the service")
        raise typer.Exit()

    project_path = Path(".")
    context = {"name": name.lower(), "class_name": name.capitalize()}

    routes_dir = project_path / "app/schemas"
    routes_dir.mkdir(parents=True, exist_ok=True)

    render_template("app/schemas/schema.py.j2", routes_dir / f"{name.lower()}.py", context)

    typer.echo(f"✅ schema `{name}` created successfully!")
