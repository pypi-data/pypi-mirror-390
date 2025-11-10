import typer
from fapi.utils.ustils import render_template, req_installer, create_venv
from pathlib import Path
create_app = typer.Typer(help="FastAPI project generator")


@create_app.command()
def create(
    project_name: str = typer.Argument(...),
    db: str = typer.Option(
        None, "--db", help="Database: sqlite or postgres", case_sensitive=False
    ),
    routes: bool = typer.Option(
        None, "--routes", help="Generate routes?"
    ),
):
    """Create a new FastAPI project"""
    project_dir = Path(project_name)

    if project_dir.exists():
        typer.echo(f"Directory {project_name} already exists!")
        raise typer.Exit()

    typer.echo(f"Creating FastAPI project: {project_name}... ✅")
    if db is None:
        use_db = typer.confirm("do you want to use a db?")
        db_choice = typer.prompt("Choose a Database (sqlite/postgres)", default="sqlite") if use_db else None
    else:
        use_db = db.lower() in ["postgres", "sqlite"]
        db_choice = db.lower()
        if not use_db: 
            typer.echo(f"Invalid DB option! {db} neither 'sqlite' not 'postgres")
            raise typer.Exit() 

    if routes is None:
        use_routes = typer.confirm("do you want to generate routes?")
    else:
        use_routes = routes

    

    context = {"project_name": project_name, "use_db":use_db, "db_choice": db_choice, "use_routes": use_routes}

    # Create folders
    (project_dir / "app").mkdir(parents=True, exist_ok=True)

    # Render templates
    render_template("app/main.py.j2", project_dir / "app/main.py", context)
    (project_dir / "app" / "core").mkdir()
    render_template("app/core/config.py.j2", project_dir / "app/core/config.py", context)
    if use_db:
        (project_dir / "app" / "models").mkdir()
        (project_dir / "app" / "schemas").mkdir()
        (project_dir / "app" / "crud").mkdir()
        render_template("app/crud/user.py.j2", project_dir / "app/crud/user.py", context)
        render_template("app/core/database.py.j2", project_dir / "app/core/database.py", context)
        render_template("app/models/user.py.j2", project_dir / "app/models/user.py", context)
        render_template("app/schemas/user.py.j2", project_dir / "app/schemas/user.py", context)
    if use_routes:
        (project_dir / "app" / "api").mkdir()
        (project_dir / "app" / "services").mkdir()
        (project_dir / "app" / "api" / "routes").mkdir()
        render_template("app/api/routes/user.py.j2", project_dir / "app/api/routes/user.py", context)
        render_template("app/api/router.py.j2", project_dir / "app/api/router.py", context)
        render_template("app/services/passwordHash.py.j2", project_dir / "app/services/passwordHash.py", context)
    render_template("requirements.txt.j2", project_dir / "requirements.txt", context)
    render_template("app/__init__.py.j2", project_dir / "app/__init__.py", context)
    # Create .env example
    (project_dir / ".env").write_text("APP_NAME=" + project_name)
    create_venv(project_dir)
    req_installer(project_dir)
    (project_dir / ".fastapi").write_text("fastapi-project")


    typer.echo("✅ Project created successfully!")
    typer.echo(f"Next steps 👉 \n")
    typer.echo(f"cd {project_name}")
    typer.echo("""activate venv: 
               linux / mac: source .venv/bin/activate
                Windows (PowerShell):
                .venv\\Scripts\\Activate.ps1

                Windows (CMD):
                .venv\\Scripts\\activate.bat
               """)
    typer.echo(f"uvicorn app.main:app --reload")
