# E2E Project — Render Ready

## Deploy on Render
1. Upload this project to a GitHub repository.
2. In Render, choose **New + → Blueprint** and select the repository.
3. Render will read `render.yaml` and use the free web service.
4. If deploying as a Web Service manually:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

## Important: SQLite
This project uses SQLite. Render's free service has an ephemeral filesystem, so database changes can be lost after a restart/redeploy.
This package is suitable for demos/testing. For persistent production data, migrate the database to PostgreSQL (or another persistent database).

## Expected Flask entry point
The Render configuration assumes the Flask application object is named `app` in `app.py`, so the start command is:
`gunicorn app:app`
