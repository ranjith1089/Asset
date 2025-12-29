# Asset Management System

A full-stack asset management system for tracking office assets (laptops, headphones, etc.) and their assignments to employees.

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Backend**: Python FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth

## Project Structure

```
├── backend/          # Python FastAPI backend
├── frontend/         # React TypeScript frontend
├── database/         # SQL schema files
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your Supabase credentials:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `SUPABASE_SERVICE_KEY`: Your Supabase service role key

6. Run the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Database Setup

1. Log into your Supabase dashboard
2. Go to SQL Editor
3. Run the SQL script from `database/schema.sql`
4. This will create all necessary tables, indexes, and RLS policies

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your configuration:
   - `VITE_SUPABASE_URL`: Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
   - `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

5. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal)

## Features

- Asset management (CRUD operations)
- Employee management
- Asset assignment tracking
- Assignment history
- Search and filter capabilities
- Dashboard with statistics

## API Endpoints

### Assets
- `GET /api/assets` - Get all assets
- `GET /api/assets/{id}` - Get asset by ID
- `POST /api/assets` - Create asset
- `PUT /api/assets/{id}` - Update asset
- `DELETE /api/assets/{id}` - Delete asset

### Employees
- `GET /api/employees` - Get all employees
- `GET /api/employees/{id}` - Get employee by ID
- `POST /api/employees` - Create employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee

### Assignments
- `GET /api/assignments` - Get all assignments
- `GET /api/assignments/{id}` - Get assignment by ID
- `POST /api/assignments` - Create assignment (assign asset)
- `PUT /api/assignments/{id}/return` - Return assigned asset

## Authentication

All API endpoints require authentication via Bearer token (Supabase JWT). The frontend handles authentication using Supabase Auth.

