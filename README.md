# E2E Project Creation - Python Demo

This is a standalone Flask + SQLite implementation based on the supplied E2E Project Creation presentation.

## Requirements
- Python 3.10+ recommended
- Internet access on first run to install Flask

## Windows
Double-click `run_windows.bat`, or:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

## macOS / Linux
```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```
Then open: http://127.0.0.1:5000

The SQLite database is created automatically as `e2e_project.db`.

## Modules
- Project dashboard
- Project creation
- Project financial KPIs
- Actions tracker
- Risk tracker
- Order-management checklist
- SAP VA01/YPO2 simulation form

This project does NOT connect to real SAP or SGV.

- Project deletion with confirmation (also removes related actions and risks)
