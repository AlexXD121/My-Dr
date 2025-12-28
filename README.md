# 🩺 My Dr - Intelligent Medical Assistant

My Dr is a modern, full-stack medical assistant application that provides AI-powered health consultations, symptom checking, medical history tracking, and health analytics. Built with React.js frontend and Python FastAPI backend with local AI integration.

## ✨ Features

- 🤖 **AI-Powered Chat**: Intelligent medical consultations with natural language processing
- 🩺 **Symptom Checker**: Advanced symptom analysis and recommendations
- 📋 **Medical History**: Comprehensive health record management
- 💊 **Drug Interactions**: Medication interaction checking and warnings
- 💡 **Health Tips**: Personalized health recommendations and tips
- 📊 **Health Analytics**: Visual health data tracking and insights
- 🌙 **Dark/Light Mode**: Beautiful theme switching with smooth transitions
- 📱 **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- 🎨 **Modern UI**: Glassmorphism design with smooth animations
- 🔊 **Voice Integration**: Speech recognition and text-to-speech capabilities
- ⚡ **Real-time Updates**: Live chat with typing indicators and animations

## 🏗️ Architecture

```
My Dr/
├── frontend/          # React.js + Vite + Tailwind CSS
├── backend/           # Python FastAPI + SQLite/PostgreSQL
├── start_my_dr.py     # Easy startup script
├── README.md          # This file
├── INSTALLATION.md    # Installation guide
└── USER_MANUAL.md     # User manual
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+
- **Git**

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd My-Dr
   ```

2. **Run the startup script**
   ```bash
   python start_my_dr.py
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

### Manual Setup

If you prefer manual setup:

1. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python migrations.py  # Initialize database
   python main.py
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📚 Documentation

- [📖 Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [👤 User Manual](USER_MANUAL.md) - Complete user guide
- [🔧 Backend Setup](backend/README.md) - Backend configuration
- [🎨 Frontend Setup](frontend/README.md) - Frontend development guide

## 🛠️ Technology Stack

### Frontend
- **React.js 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Icons** - Beautiful icon library
- **React Markdown** - Markdown rendering

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite/PostgreSQL** - Database options
- **Pydantic** - Data validation and serialization
- **CORS** - Cross-origin resource sharing
- **Uvicorn** - ASGI server

## 🎨 Design System

- **Color Scheme**: Blue, Black, and Gray palette
- **Typography**: Inter font family
- **Animations**: 60 FPS smooth transitions
- **Glassmorphism**: Modern glass-like UI elements
- **Responsive**: Mobile-first design approach

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting for API endpoints
- CORS configuration
- Environment variable protection
- SQL injection prevention

## 🌟 Key Highlights

- **Modern Design**: Beautiful glassmorphism UI with smooth animations
- **AI Integration**: Intelligent medical assistance and recommendations
- **Comprehensive Features**: Complete health management suite
- **Performance Optimized**: Fast loading and smooth interactions
- **Accessibility**: WCAG compliant with keyboard navigation
- **Cross-Platform**: Works on all devices and browsers

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, email support@mydocai.com or create an issue in the repository.

---

**Made with ❤️ for better healthcare accessibility**