# Compiler Studio

Web UI for a C compiler front end (Flex + Bison): lexical → syntax → semantic → three-address code.

## Run locally
    docker build -t compiler-studio . && docker run -p 8000:8000 compiler-studio
Open http://localhost:8000

## Deploy (free live URL)
Push to GitHub, create a **Web Service** on Render (or Railway/Fly.io) from the repo, runtime **Docker**. One container serves both the API (`POST /api/compile`) and the UI.

## Layout
- `compiler/` – your Lex/Yacc sources, one folder per phase
- `backend/app.py` – Flask API; runs each phase binary in a temp dir and returns stdout + generated tables
- `frontend/index.html` – single-file UI, no build step