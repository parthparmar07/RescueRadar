# RescueRadar Flask Backend

A Flask-based REST API backend for the RescueRadar application.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `.env.example` to `.env` and update with your API keys.

3. **Run the Flask server:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check service health

### Reports
- `POST /api/save-report` - Save a new report
- `GET /api/reports/active` - Get all active reports

### AI Analysis
- `POST /api/ai-analysis` - Analyze report using AI

### Notifications
- `POST /api/email-notify` - Send email notification
- `POST /api/whatsapp-notify` - Send WhatsApp notification
- `GET /api/generate-qr` - Generate QR code

### File Upload
- `POST /api/upload-image` - Upload image files
- `GET /api/uploads/<filename>` - Serve uploaded files

## Project Structure

```
flask-backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── routes/            # API route modules
│   ├── ai_analysis.py
│   ├── reports.py
│   ├── notifications.py
│   └── upload.py
└── uploads/           # Uploaded files directory
```

## Configuration

The backend uses the same environment variables as the Next.js frontend for consistency.

## CORS

CORS is enabled for all routes to allow frontend access from different origins.
