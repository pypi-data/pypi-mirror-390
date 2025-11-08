## SQLite Web Viewer

A lightweight web UI to browse and edit SQLite databases in a directory.

### Install

- From PyPI (recommended):

```
pip install sqlitewebviewer
```

- From source (this repo):

```
pip install .
```

### Run

Run the server in the directory that contains your SQLite files (it scans the current working directory recursively):

```
sqlitewebviewer
```

Then open `http://localhost:8080`.

#### Options

You can change host/port and enable debug via flags or environment variables:

```
sqlitewebviewer --host 127.0.0.1 --port 8081 --debug
```

Or using env vars:

```
HOST=127.0.0.1 PORT=8081 DEBUG=1 sqlitewebviewer
```

- If port 8080 is in use, either choose another port (e.g. `--port 0` for an ephemeral port or `--port 8081`) or free it:

```
lsof -i :8080
kill <PID>
```

### Features

- Auto-detects SQLite files (`.db`, `.sqlite`, `.sqlite3`) in the working directory and subfolders
- Browse tables, inline edit cells, insert/delete rows, export CSV
- SQL query editor with results table

### Publish to PyPI (maintainers)

1) Build distributions:

```
python -m pip install --upgrade build twine
python -m build
```

2) Upload:

```
python -m twine upload dist/*
```

Ensure `version` in `setup.py` is incremented before releasing.

