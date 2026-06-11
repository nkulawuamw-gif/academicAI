# AcademAI - AI Academic Assistant

A full-stack AI-powered academic assistant SaaS application built with Next.js 15 and FastAPI.

## Tech Stack

### Frontend
- **Next.js 15** with App Router
- **React 19** + TypeScript
- **Tailwind CSS** for styling
- **ShadCN UI** component library
- **Zustand** for state management
- **TanStack Query** for server state
- **Zod** for validation

### Backend
- **FastAPI** (Python 3.12)
- **SQLAlchemy** async ORM
- **PostgreSQL** database
- **Alembic** for migrations
- **ChromaDB** vector database
- **JWT + Google OAuth** authentication
- **OpenAI API** for AI features

## Features

1. **Authentication** - Email/password + Google OAuth, password reset, profile management
2. **AI Chat Assistant** - Multi-turn conversations with streaming responses
3. **Research Assistant** - Web search, academic sources, literature reviews
4. **Writing Assistant** - Essays, reports, research papers, outlines
5. **Paraphrasing Tool** - Academic, professional, simplification modes
6. **Citation Generator** - APA 7, MLA, Harvard, Chicago, IEEE
7. **Study Tools** - Quiz generator, flashcards, note summarizer, study planner
8. **Document Processing** - PDF/DOCX upload, text extraction, RAG Q&A
9. **Admin Dashboard** - User management, analytics

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Security, exceptions, logging
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── lib/               # API client, utilities
│   ├── store/             # Zustand stores
│   ├── types/             # TypeScript types
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL 16
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Copy environment variables
cp .env.local.example .env.local
# Edit .env.local with your settings

# Start dev server
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

### Environment Variables

#### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/academic_assistant
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OPENAI_API_KEY=your-openai-api-key
```

#### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/google` - Google OAuth
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/forgot-password` - Forgot password
- `POST /api/v1/auth/reset-password` - Reset password
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/profile` - Update profile

### Chat
- `GET /api/v1/chat/conversations` - List conversations
- `POST /api/v1/chat/conversations` - Create conversation
- `GET /api/v1/chat/conversations/:id` - Get conversation
- `POST /api/v1/chat/conversations/:id/messages` - Send message

### Research
- `POST /api/v1/research/search` - Search web sources
- `POST /api/v1/research/literature-review` - Generate lit review

### Writing
- `POST /api/v1/writing/generate` - Generate content
- `POST /api/v1/writing/outline` - Generate outline

### Other
- `POST /api/v1/paraphrase` - Paraphrase text
- `POST /api/v1/citations/generate` - Generate citation
- `POST /api/v1/study/quizzes/generate` - Generate quiz
- `POST /api/v1/documents/upload` - Upload document

## Deployment

### Frontend (Netlify)
```bash
cd frontend
npm run build
# Deploy the .next folder to Netlify
```

### Backend (Render)
```bash
# Deploy the backend/ directory to Render as a Web Service
# Set the start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database (Supabase)
- Create a Supabase project
- Use the provided PostgreSQL connection string

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend typecheck
cd frontend
npm run typecheck
```

## License

MIT
