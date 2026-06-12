<div align="center">

# ⚡ SnippetVault

### Your Personal Code Library — Store, Organize & Share Snippets Beautifully

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

<br/>

![SnippetVault Banner](https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&h=400&fit=crop&q=80)

<br/>

[🚀 Live Demo](#) · [🐛 Report Bug](../../issues) · [✨ Request Feature](../../issues)

</div>

---

## 📌 What is SnippetVault?

**SnippetVault** is a full-stack SaaS developer tool that lets you store, organize, and share code snippets across every language and framework. Built for developers who value speed, clarity, and clean UI.

> Think GitHub Gist — but with a beautiful UI, instant search, real-time syntax highlighting, and one-click public sharing.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **GitHub OAuth** | One-click login with your GitHub account |
| ⚡ **Instant Search** | Full-text PostgreSQL search across all snippets |
| 🎨 **Syntax Highlighting** | 20+ languages powered by Shiki |
| 🔗 **One-click Share** | Public links with view count tracking |
| 🏷️ **Tags & Filters** | Organize snippets with tags and language filters |
| 🔒 **Private Snippets** | Control what's public and what stays private |
| 📊 **Analytics** | Track views and stars on your snippets |
| 🚦 **Rate Limiting** | Redis sliding window — production-grade protection |
| 🗃️ **Free & Pro Plans** | Free tier (50 snippets) + Pro (unlimited) |

---

## 🛠️ Tech Stack

### Frontend
- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS** — utility-first styling
- **Framer Motion** — smooth animations
- **Shiki** — syntax highlighting

### Backend
- **FastAPI** — high performance Python API
- **PostgreSQL** — primary database with full-text search (tsvector)
- **Redis (Upstash)** — caching + rate limiting (sliding window)
- **SQLAlchemy (Async)** + **Alembic** — ORM + migrations
- **JWT Auth** + **GitHub OAuth** — secure authentication
- **Nanoid** — unique share IDs

### DevOps
- **Render** — backend deployment
- **Netlify** — frontend deployment
- **Supabase** — managed PostgreSQL
- **Upstash** — managed Redis

---

## 🏗️ Architecture

```
snippetvault/
├── snippetvault-frontend/       # React + Vite app
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Route pages
│   │   └── hooks/               # Custom React hooks
│
└── snippetvault-backend/        # FastAPI app
    └── app/
        ├── routers/             # API route handlers
        ├── models/              # SQLAlchemy ORM models
        ├── schemas/             # Pydantic validation schemas
        ├── services/            # Business logic layer
        ├── middleware/          # Rate limiting + logging
        └── core/                # Security + dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- Node.js 18+
- PostgreSQL 15
- Redis

### Backend Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/snippetvault.git
cd snippetvault/snippetvault-backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Fill in your values (see Environment Variables section below)

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

API will be live at: `http://localhost:8000`
Swagger docs at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd snippetvault/snippetvault-frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be live at: `http://localhost:5173`

---

## 🔑 Environment Variables

Create a `.env` file in `snippetvault-backend/`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost/snippetvault
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secret-key-minimum-32-characters
JWT_EXPIRE_DAYS=7

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:5173/auth/callback

ALLOWED_ORIGINS=http://localhost:5173
ENVIRONMENT=development
```

> **How to get GitHub OAuth credentials:**
> Go to GitHub → Settings → Developer Settings → OAuth Apps → New OAuth App

---

## 📡 API Endpoints

### Auth
```
GET  /auth/github              → Redirect to GitHub OAuth
GET  /auth/github/callback     → Exchange code for JWT
GET  /auth/me                  → Get current user
POST /auth/logout              → Blacklist JWT token
```

### Snippets
```
GET    /snippets               → List my snippets (paginated + filtered)
POST   /snippets               → Create new snippet
GET    /snippets/{id}          → Get single snippet
PUT    /snippets/{id}          → Update snippet
DELETE /snippets/{id}          → Delete snippet
GET    /snippets/search?q=     → Full-text search
```

### Public
```
GET  /s/{share_id}             → View public snippet (no auth)
```

### Stars
```
POST   /snippets/{id}/star     → Star a snippet
DELETE /snippets/{id}/star     → Unstar a snippet
```

---

## ⚡ Rate Limiting

| Type | Limit |
|---|---|
| Authenticated users | 200 requests / hour |
| Unauthenticated (IP) | 30 requests / hour |
| POST /snippets | 20 requests / hour |
| Public snippet view | 100 requests / hour per IP |

Rate limits use **Redis sliding window algorithm** for accuracy.

---

## 🗄️ Database Schema

```sql
Users        → id, github_id, username, avatar_url, plan, snippets_count
Snippets     → id, user_id, title, code, language, tags[], is_public, share_id, view_count, star_count
Stars        → id, user_id, snippet_id
```

Full-text search index on `snippets(title, description, code)` using PostgreSQL `tsvector`.

---

## 🌐 Deployment

### Backend → Render
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo
4. Set environment variables in Render dashboard
5. Build command: `pip install -r requirements.txt && alembic upgrade head`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend → Netlify
1. Go to [netlify.com](https://netlify.com) → Add New Site
2. Connect your GitHub repo
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Set `VITE_API_URL` environment variable to your Render backend URL

### Database → Supabase (Free)
1. Create project at [supabase.com](https://supabase.com)
2. Copy the connection string to `DATABASE_URL`

### Redis → Upstash (Free)
1. Create database at [upstash.com](https://upstash.com)
2. Copy Redis URL to `REDIS_URL`

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork the repo
# Create your feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m 'Add amazing feature'

# Push to branch
git push origin feature/amazing-feature

# Open a Pull Request
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Jayesh Bhoge**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/yourusername)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-FF5722?style=for-the-badge&logo=google-chrome&logoColor=white)](https://yourportfolio.com)

---

<div align="center">

⭐ **If you found this project useful, please give it a star!** ⭐

*Built with ❤️ by Jayesh Bhoge*

</div>
