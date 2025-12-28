# 🎤 Female Voice Integration for MyDoc AI

This guide explains how to set up and use the sweet female voice feature for your MyDoc AI Medical Assistant.

## 🌟 Features

- **3 Beautiful Female Voices**: Jenny (caring), Aria (gentle), Maya (professional)
- **Medical-Optimized**: Specially tuned for healthcare conversations
- **Emotional Intelligence**: Caring tone with medical context awareness
- **High Quality**: Uses Coqui TTS for natural-sounding speech
- **Customizable**: Adjustable speed, pitch, and emotion settings

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
# Run the setup script
python setup_female_voice_server.py

# Start the TTS server
# Windows:
tts_server/start_tts_server.bat

# Unix/Linux/Mac:
./tts_server/start_tts_server.sh
```

### Option 2: Manual Setup

1. **Install Coqui TTS**:
   ```bash
   pip install TTS>=0.22.0 torch torchaudio flask flask-cors
   ```

2. **Download Models**:
   ```bash
   # Jenny voice (sweet medical assistant)
   python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/tacotron2-DDC')"
   
   # Aria voice (gentle healthcare)
   python -c "from TTS.api import TTS; TTS('tts_models/en/vctk/vits')"
   
   # Maya voice (professional AI)
   python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/glow-tts')"
   ```

3. **Start Server**:
   ```bash
   cd tts_server
   python tts_server.py
   ```

## 🎯 Voice Personalities

### 👩‍⚕️ Jenny - Sweet Medical Assistant
- **Best for**: General medical consultations
- **Characteristics**: Warm, caring, professional, clear
- **Tone**: Empathetic and nurturing
- **Use case**: Primary voice for patient interactions

### 🌸 Aria - Gentle Healthcare Voice
- **Best for**: Sensitive health topics
- **Characteristics**: Gentle, reassuring, empathetic
- **Tone**: Soft and soothing
- **Use case**: Mental health, chronic conditions

### 🧠 Maya - Smart Medical AI
- **Best for**: Technical medical information
- **Characteristics**: Intelligent, friendly, trustworthy
- **Tone**: Professional yet approachable
- **Use case**: Medical explanations, drug information

## ⚙️ Configuration

### Frontend Settings

The female voice can be customized through the UI:

1. **Access Settings**: Click the pink heart icon in voice controls
2. **Choose Voice**: Select Jenny, Aria, or Maya
3. **Set Emotion**: Caring, Professional, Friendly, or Gentle
4. **Adjust Speed**: 0.5x to 1.5x (0.9x recommended for medical)
5. **Tune Pitch**: 0.8 to 1.4 (1.1 recommended for feminine tone)

### Backend Configuration

Update your `.env` file:

```bash
# Female Voice TTS Server
FEMALE_VOICE_TTS_URL=http://localhost:5002
FEMALE_VOICE_ENABLED=true
FEMALE_VOICE_DEFAULT_MODEL=jenny
FEMALE_VOICE_DEFAULT_EMOTION=caring
```

## 🔧 API Usage

### Test Voice Endpoint
```bash
curl -X POST http://localhost:5002/api/test \
  -H "Content-Type: application/json" \
  -d '{"voice": "jenny"}'
```

### Synthesize Speech
```bash
curl -X POST http://localhost:5002/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! How can I help you with your health today?",
    "model_name": "jenny",
    "speed": 0.9,
    "pitch": 1.1
  }' \
  --output speech.wav
```

### Get Available Voices
```bash
curl http://localhost:5002/api/voices
```

## 🎨 Frontend Integration

The female voice service is automatically integrated into your existing voice controls:

```javascript
import femaleVoiceService from '../services/femaleVoiceService';

// Speak with female voice
await femaleVoiceService.speak("Hello there! How are you feeling today?", {
  model: 'jenny',
  speed: 0.9,
  pitch: 1.1,
  emotion: 'caring'
});

// Test different voices
await femaleVoiceService.testVoice('aria');
```

## 🔍 Troubleshooting

### Common Issues

1. **Server Won't Start**:
   ```bash
   # Check Python version (3.8+ required)
   python --version
   
   # Install missing dependencies
   pip install -r tts_server/requirements.txt
   ```

2. **Models Not Loading**:
   ```bash
   # Re-download models
   python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/tacotron2-DDC', progress_bar=True)"
   ```

3. **Audio Quality Issues**:
   - Increase sample rate in config.json
   - Adjust speed/pitch settings
   - Check system audio drivers

4. **Performance Issues**:
   - Use GPU acceleration if available
   - Reduce model complexity
   - Cache frequently used phrases

### Health Check

```bash
# Test server health
curl http://localhost:5002/health

# Expected response:
{
  "status": "healthy",
  "models_loaded": 3,
  "available_voices": ["jenny", "aria", "maya"]
}
```

## 🚀 Production Deployment

### Docker Setup

```dockerfile
# Add to your existing Dockerfile
FROM python:3.9-slim

# Install TTS dependencies
RUN pip install TTS torch torchaudio flask flask-cors

# Copy TTS server
COPY tts_server/ /app/tts_server/
WORKDIR /app/tts_server

# Download models (optional - can be done at runtime)
RUN python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/tacotron2-DDC')"

# Expose port
EXPOSE 5002

# Start server
CMD ["python", "tts_server.py"]
```

### Environment Variables

```bash
# Production settings
FEMALE_VOICE_TTS_URL=https://tts.yourdomain.com
FEMALE_VOICE_CACHE_ENABLED=true
FEMALE_VOICE_MAX_TEXT_LENGTH=1000
FEMALE_VOICE_RATE_LIMIT=60
```

## 📊 Performance Optimization

### Caching Strategy

```javascript
// Enable caching for frequently used phrases
const commonPhrases = [
  "Hello! How can I help you today?",
  "I understand your concern.",
  "Please consult with a healthcare professional.",
  "Take care of yourself!"
];

// Pre-generate and cache
commonPhrases.forEach(phrase => {
  femaleVoiceService.speak(phrase, { cache: true });
});
```

### GPU Acceleration

```python
# Enable GPU in tts_server.py
import torch

# Check for CUDA
if torch.cuda.is_available():
    device = "cuda"
    print("🚀 Using GPU acceleration")
else:
    device = "cpu"
    print("💻 Using CPU")

# Load models with GPU support
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
```

## 🎯 Best Practices

### Medical Context Optimization

1. **Use Jenny for general consultations** - warm and professional
2. **Use Aria for sensitive topics** - gentle and reassuring  
3. **Use Maya for technical explanations** - clear and intelligent
4. **Adjust speed to 0.8-0.9x** for complex medical terms
5. **Use caring emotion** for patient interactions
6. **Add pauses** before important medical information

### Text Processing

```javascript
// Optimize text for female voice
const medicalText = "You should take acetaminophen 500mg twice daily.";

// Processed version
const processedText = "I would recommend that you take acetaminophen, that's 500 milligrams, twice daily for your comfort.";
```

## 🔐 Security Considerations

1. **Rate Limiting**: Limit requests per user/IP
2. **Text Validation**: Sanitize input text
3. **HTTPS**: Use SSL in production
4. **Authentication**: Secure API endpoints
5. **Content Filtering**: Block inappropriate content

## 📈 Monitoring

### Health Metrics

- Server uptime and response time
- Model loading status
- Audio generation success rate
- Memory and CPU usage
- Request volume and patterns

### Logging

```python
# Enhanced logging in tts_server.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tts_server.log'),
        logging.StreamHandler()
    ]
)
```

## 🎉 Success Metrics

After implementing the female voice:

- ✅ **User Engagement**: More natural conversations
- ✅ **Accessibility**: Better for visually impaired users  
- ✅ **Trust**: Caring tone builds patient confidence
- ✅ **Professionalism**: Medical-optimized pronunciation
- ✅ **Personalization**: Multiple voice personalities

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review server logs: `tail -f tts_server/tts_server.log`
3. Test with curl commands above
4. Verify model downloads completed
5. Check system requirements (Python 3.8+, sufficient RAM)

---

**Enjoy your new sweet female AI medical assistant voice! 🩺💕**