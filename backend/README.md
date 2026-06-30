# EventWall Backend Configuration

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the `backend` directory:

```env
DEBUG=True
FIREBASE_PROJECT_ID=eventwall-project
FIREBASE_CREDENTIALS_PATH=./firebase-key.json
DATABASE_URL=sqlite:///./eventwall.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Firebase Setup
- Download your Firebase credentials JSON from Google Cloud Console
- Save it as `firebase-key.json` in the backend directory

### 4. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new organization
- `POST /api/auth/login` - Login organization

### Events
- `POST /api/events/` - Create event
- `GET /api/events/` - List events
- `GET /api/events/{event_id}` - Get event details
- `PUT /api/events/{event_id}` - Update event
- `DELETE /api/events/{event_id}` - Delete event

### Devices
- `POST /api/devices/generate-join-code` - Generate join code
- `POST /api/devices/join` - Device joins with code
- `GET /api/devices/` - List devices
- `GET /api/devices/{device_id}` - Get device details
- `DELETE /api/devices/{device_id}` - Revoke device

## Architecture

```
backend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── database.py      # DB setup
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── utils.py         # Utilities
│   ├── firebase_init.py # Firebase setup
│   └── routes/
│       ├── auth.py      # Auth endpoints
│       ├── events.py    # Event endpoints
│       └── devices.py   # Device endpoints
├── requirements.txt
├── Dockerfile
└── README.md
```

## Next Steps

1. **AI Wallpaper Generation** - Integrate Replicate/Vertex AI
2. **Device Sync API** - Real-time wallpaper sync
3. **Background Tasks** - Celery for background jobs
4. **Firebase Firestore** - Real-time device listeners
