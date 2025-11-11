# FastAPI Project Generator CLI

A CLI tool that scaffolds FastAPI projects with optional database and API structure.

---

## ✅ Features

| Feature                    | Description                                     |
| -------------------------- | ----------------------------------------------- |
| Generate FastAPI project   | Creates a full FastAPI folder structure         |
| Optional Database          | Create project with or without SQLAlchemy setup |
| Auto-creates virtualenv    | Creates `.venv` inside the project              |
| Auto-installs requirements | Installs dependencies based on options          |
| Jinja2 Templates           | Clean and flexible template system              |
| Developer friendly         | Simple prompts & automatic setup                |
| CLI `add` commands         | Add routes, models, schemas, crud, services     |

---

## 📂 Project Output Structure

When DB and routes are enabled:

```
project_name/
 ├─ app/
 │  ├─ main.py
 │  ├─ core/
 │  │   └─ config.py
 │  ├─ models/
 │  │   └─ user.py
 │  ├─ schemas/
 │  │   └─ user.py
 │  ├─ crud/
 │  │   └─ user.py
 │  ├─ services/
 │  │   └─ example.py
 │  ├─ api/
 │  │   └─ router.py
 │  └─ __init__.py
 ├─ .fastapi                  # internal flag to detect project
 ├─ .env
 ├─ requirements.txt
 └─ .venv/
```

If database or routes are disabled, the tool skips those folders.

---

## 🧰 Installation

### Clone Repo

```bash
pip install fapier
```
or
```bash
pipx install fapier
```

> Requires Python 3.10+

---

## Usage

### Create a project

```bash
fapi create myProject
```

### Answer prompts

Example interaction:

```
Do you want to use a DB? [y/n]: y
Choose a Database (sqlite/postgres) [sqlite]: sqlite
Do you want to generate routes? [y/n]: y
```

or simply run

```bash
python cli.py myproject --db sqlite --routes
```

### Add new components

```bash
fapi add route product
fapi add model product --schema --crud
fapi add service payment
fapi add schema product
fapi add crud product

```

> Auto-detects if you're inside a FastAPI project using `.fastapi`

---

## 🏁 Run the project

```bash
cd myproject
source .venv/bin/activate   # Linux/Mac
# or .venv\Scripts\activate on Windows

uvicorn app.main:app --reload
```

---

## 📌 Roadmap

| Feature                | Status     |
| ---------------------- | ---------- |
| Basic FastAPI scaffold | ✅ Done     |
| Optional DB            | ✅ Done     |
| Optional API           | ✅ Done     |
| `fapi add` commands    | ✅ Done     |
| Auto router import     | 🔜 Planned |
| Alembic migrations     | 🔜 Planned |
| Docker support         | 🔜 Planned |
| Publish on PyPI        | ✅ Done    |

---

## 🤝 Contributing

Pull requests are welcome! 👐

---

⭐ If you like this tool, give the repo a star!
