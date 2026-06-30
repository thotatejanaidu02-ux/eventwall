# EventWall - Enterprise Wallpaper Management System

A comprehensive, multi-platform wallpaper management system with:
- **Python FastAPI Backend** - Scalable API with Firebase integration
- **React Frontend** - Modern admin dashboard
- **Flutter Client** - Cross-platform endpoint for wallpaper rotation

## Project Structure

```
eventwall/
├── backend/              # Python FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React admin dashboard (TBD)
└── flutter_client/       # Flutter mobile/desktop client (TBD)
```

## Quick Start

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Update .env with your Firebase credentials
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`

## Architecture Overview

### Parent (Admin) Node
- Web/Desktop dashboard built with React
- Authentication via Firebase Auth
- Event scheduling and management
- Device join code generation
- AI wallpaper generation integration
- Real-time device monitoring

### Child (Endpoint) Node
- Lightweight Flutter client
- Silent background service
- Real-time Firebase stream listening
- Native OS wallpaper APIs
- Offline caching

## Key Features

✅ Enterprise authentication & authorization  
✅ Join code device onboarding  
✅ Real-time event syncing via Firebase  
✅ AI wallpaper generation (Replicate/Vertex AI)  
✅ Cross-platform support (Windows, macOS, iOS, Android)  
✅ Background processing with workmanager  
✅ Offline wallpaper caching  
✅ Device revocation & management  

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Firebase Admin SDK, JWT
- **Frontend:** React, TypeScript (TBD)
- **Mobile:** Flutter, Firebase, workmanager
- **AI:** Replicate/Google Vertex AI
- **Database:** Firebase Firestore + SQLite/PostgreSQL
- **Cache:** Redis (optional)

## Documentation

- [Backend Setup](./backend/README.md)
- [Frontend Setup](./frontend/README.md) (TBD)
- [Flutter Client Setup](./flutter_client/README.md) (TBD)

## API Documentation

Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

## License

MIT

## Contributing

Pull requests welcome! Please follow the existing code style and add tests for new features.
