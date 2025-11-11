# Automation-Lib Python Package

This repository contains the `automation-lib` Python package, a collection of automation modules for document processing.

## Package Creation and Distribution

This section provides instructions on how to build and distribute this Python package.

### 1. Build the Package

To build the source distribution and wheel files for the package, follow these steps:

1.  **Navigate to the project root:**
    ```bash
    cd /path/to/your/automation-lib-repo
    ```
    (Note: If you are already in the root directory of this repository, you can skip this step.)

2.  **Install `build` (if not already installed):**
    ```bash
    uv pip install build
    ```

3.  **Create the Source Distribution and Wheel:**
    ```bash
    uv build
    ```
    After running this command, the created files (e.g., `automation_lib-0.1.0-py3-none-any.whl` and `automation_lib-0.1.0.tar.gz`) will be located in the `dist/` directory.

### 2. Local Installation

You can install this package locally in another Python project for development or testing purposes.

1.  **Navigate to your other project directory:**
    ```bash
    cd /path/to/your/other-project
    ```

2.  **Create a virtual environment (if not already done) and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the package from the `dist/` directory:**
    ```bash
    uv pip install /path/to/your/new/automation-lib-repo/dist/automation_lib-0.1.0-py3-none-any.whl
    ```
    Replace `/path/to/your/new/automation-lib-repo` with the actual path to this repository on your system.

After installation, you can import modules from `automation_lib` as usual:
```python
from automation_lib.llm_prompt import ...
from automation_lib.transcription import ...
```

### 3. Release-Prozess

Der Release-Prozess für dieses Projekt ist automatisiert und erfolgt über das Makefile. Hier ist eine Übersicht über die notwendigen Schritte:

#### Vorbereitung vor dem Release

**Wichtig:** Vor dem Release müssen alle Änderungen eingecheckt und gepusht sein:

1. **Alle Änderungen committen:**
   ```bash
   git add .
   git commit -m "feat: Beschreibung der Änderungen"
   ```

2. **Änderungen pushen:**
   ```bash
   git push origin main
   ```

3. **Status überprüfen:**
   ```bash
   git status
   # Sollte "working tree clean" anzeigen
   ```

#### Release durchführen

Nach der Vorbereitung kann der Release über das Makefile angestoßen werden:

```bash
# Patch-Version erhöhen (0.1.0 → 0.1.1) - für Bugfixes
make publish-github

# Minor-Version erhöhen (0.1.0 → 0.2.0) - für neue Features
make publish-github-minor

# Major-Version erhöhen (0.1.0 → 1.0.0) - für Breaking Changes
make publish-github-major

# Test-Durchlauf ohne Änderungen (Dry-Run)
make publish-github-dry
```

#### Was passiert beim Release?

Der automatisierte Release-Prozess führt folgende Schritte aus:

1. **Versionsnummer aktualisieren** in `pyproject.toml`
2. **Paket bauen** mit `make build`
3. **Git-Commit erstellen** mit der neuen Version
4. **Git-Tag erstellen** (z.B. `v1.0.0`)
5. **Änderungen und Tags zu GitHub pushen**

#### Manuelle Publishing-Optionen

Für erweiterte Kontrolle können Sie auch das Publishing-Script direkt verwenden:

```bash
# Grundlegende Verwendung
python3 scripts/publish_to_github.py

# Spezifischen Versionstyp angeben
python3 scripts/publish_to_github.py --version-type minor

# Explizite Version setzen
python3 scripts/publish_to_github.py --version 1.2.3

# Dry-Run (Simulation ohne Änderungen)
python3 scripts/publish_to_github.py --dry-run

# Alle Prompts automatisch bestätigen
python3 scripts/publish_to_github.py --auto-confirm
```

#### Installation nach dem Release

Nach dem Release kann das Paket von GitHub installiert werden:

```bash
# Neueste Version
uv pip install git+https://github.com/jakobwowy/automation_lib.git#egg=automation-lib

# Spezifische Version
uv pip install git+https://github.com/jakobwowy/automation_lib.git@v1.0.0#egg=automation-lib
```

### 4. Private Package Distribution

For private distribution within an organization, consider the following options:

*   **Private PyPI Server:** Solutions like DevPI or Artifactory can host your private Python packages.
*   **Direct Installation from Git Repository:** You can install directly from a Git repository using `uv add git+https://github.com/jakobwowy/automation_lib.git#egg=automation-lib`.
*   **Local Wheel File:** For internal use, direct installation of the `.whl` file (as described in "Local Installation") is often sufficient.
