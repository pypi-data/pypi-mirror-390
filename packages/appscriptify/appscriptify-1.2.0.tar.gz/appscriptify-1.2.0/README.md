# AppScriptify — Login template (simple)

This small project provides a basic login/signup template using Flask and MongoDB (via Motor). It stores users in a MongoDB collection and uses secure password hashing (PBKDF2). The login can accept either username or email.

## What it uses

- Flask — web framework
- Motor (async MongoDB driver) — async access to MongoDB
- python-dotenv — load environment variables

## Files of interest

- `appscriptify/appscriptify/templates/login/app.py` — main Flask app used in this template
- `appscriptify/appscriptify/templates/login/database.py` — async database helpers (Motor)
- `config.json` — contains database/collection names (already present in the repo)
- `templates/` and `static/` — UI HTML/CSS/JS

## Environment variables

Create a `.env` file in the project root with at least:

MONGO_URI="your_mongo_connection_string"

Example `.env` content:

```
MONGO_URI="mongodb+srv://testuser:<password>@testdb.ktuizkl.mongodb.net/?appName=TestDB"
```

Also ensure `config.json` (already present) contains the database and collection names. Example values are:

```
{
  "users_database": "usersDB",
  "users_collection": "users"
}
```

Change `config.json` if needed.

## Install

1. (Optional) Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run (development)

Open a terminal and run the Flask app file used in the template. From the repository root you can run:

```powershell
python app.py
```

This will start Flask's built-in server on `http://127.0.0.1:5000` by default.

Alternatively, you can set FLASK_APP and use `flask run` after setting the working directory appropriately.

## Cookies & Sessions

- The app sets HTTP-only cookies for username/email by default (good for preventing JavaScript access).
- In development the cookie `secure` flag is set to `False` to allow non-HTTPS testing. In production change it to `True`.
- The app also stores minimal session info using Flask's `session` (server-side cookie signing). Make sure `app.secret_key` is set in production using an environment variable.

## Notes and security

- Passwords are hashed with PBKDF2 + SHA256 via Python's `hashlib` and stored as base64(salt + hash). This is reasonably secure for a small project but using a well-maintained library (like `passlib`) is recommended for production.
- Motor is async; the example app uses a single event loop and runs async DB calls from synchronous routes. For production consider using an async-capable web server/framework (Quart/FastAPI) or rewrite routes as fully sync using `pymongo`.
- Make sure your MongoDB connection string is secure and credentials are not committed to the repo.

## Next steps (suggested)

- Add a `/logout` route that clears cookies and session (I can add that for you).
- Add CSRF protection (e.g., Flask-WTF or a middleware) for forms.
- Replace manual cookie handling with Flask's session-related features or a secure server-side session store.
- Add tests for signup/login flows.
