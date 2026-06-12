# SnippetVault Backend

This is the FastAPI backend for the SnippetVault code snippet manager SaaS.

## LOCAL SETUP:
1. Install PostgreSQL locally and create database:
   ```bash
   psql -U postgres
   CREATE DATABASE snippetvault;
   ```

2. Install Redis locally:
   - Windows: download from github.com/microsoftarchive/redis
   - Mac: `brew install redis && brew services start redis`
   - Linux: `sudo apt install redis-server`

3. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # (Windows)
   source venv/bin/activate     # (Mac/Linux)
   pip install -r requirements.txt
   ```

4. Create .env file from .env.example and fill values:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost/snippetvault
   REDIS_URL=redis://localhost:6379
   JWT_SECRET=your-super-secret-min-32-chars
   GITHUB_CLIENT_ID=xxx
   GITHUB_CLIENT_SECRET=xxx
   GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
   ALLOWED_ORIGINS=http://localhost:3000
   ENVIRONMENT=development
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start server:
   ```bash
   uvicorn app.main:app --reload
   ```
