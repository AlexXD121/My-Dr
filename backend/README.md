# MyDoc AI Backend

A FastAPI-based backend for the MyDoc AI medical assistant application with local AI integration.

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start Jan AI:**
   - Open Jan AI application
   - Load the Llama 3.2 3B model
   - Enable API server
   - Set API key to: `mydoc-ai-key`

4. **Run the backend:**
```bash
uvicorn main:app --reload
```

## 🩺 Features

- **Local AI Integration**: Uses Jan AI for private medical consultations
- **Medical Safety**: Emergency detection and appropriate responses
- **Professional Guidance**: Evidence-based medical information
- **Conversation History**: Track medical consultations
- **Export Functionality**: Export conversation data
- **Security**: Rate limiting and CORS protection

## 📋 API Endpoints

- `POST /chat` - Medical consultation with AI
- `GET /conversations` - Get conversation history
- `POST /export` - Export conversations
- `GET /health` - Health check
- `GET /user/profile` - User profile (demo mode)

## ⚙️ Configuration

Key settings in `.env`:
- `USE_LOCAL_AI=true` - Enable Jan AI integration
- `JAN_URL=http://localhost:1337` - Jan AI server URL
- `JAN_MODEL=Llama-3_2-3B-Instruct-IQ4_XS` - Model name
- `JAN_API_KEY=mydoc-ai-key` - Authentication key

## 🔧 Local AI Setup

The backend prioritizes local AI (Jan AI) for privacy and speed:
1. Jan AI (Primary) - Local Llama 3.2 3B model
2. Perplexity API (Fallback)
3. Hugging Face (Fallback)

## 🛡️ Security Features

- JWT authentication
- Rate limiting
- CORS protection
- Input validation
- Medical emergency detection

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── local_ai.py          # Jan AI integration
├── mydoc.py             # Medical consultation logic
├── medical_api.py       # Medical endpoints
├── conversation_api.py  # Chat handling
├── export_api.py        # Data export
├── models.py            # Database models
├── database.py          # Database setup
├── middleware.py        # Security middleware
├── validation.py        # Input validation
└── requirements.txt     # Dependencies
```