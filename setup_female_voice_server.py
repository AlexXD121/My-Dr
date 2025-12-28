#!/usr/bin/env python3
"""
Setup script for Female Voice TTS Server
Installs and configures Coqui TTS with sweet female voices
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class FemaleVoiceServerSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tts_dir = self.project_root / "tts_server"
        self.models_dir = self.tts_dir / "models"
        
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
        
    def run_command(self, command, cwd=None):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.project_root,
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {command}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            return None
            
    def check_python_version(self):
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log("Python 3.8+ is required for Coqui TTS", "ERROR")
            return False
        self.log(f"Python {version.major}.{version.minor} detected ✓")
        return True
        
    def install_coqui_tts(self):
        """Install Coqui TTS and dependencies"""
        self.log("Installing Coqui TTS...")
        
        # Create virtual environment
        if not (self.tts_dir / "venv").exists():
            self.log("Creating virtual environment...")
            if not self.run_command(f"python -m venv {self.tts_dir}/venv"):
                return False
                
        # Activate virtual environment and install packages
        if os.name == 'nt':  # Windows
            pip_cmd = f"{self.tts_dir}/venv/Scripts/pip"
            python_cmd = f"{self.tts_dir}/venv/Scripts/python"
        else:  # Unix/Linux/Mac
            pip_cmd = f"{self.tts_dir}/venv/bin/pip"
            python_cmd = f"{self.tts_dir}/venv/bin/python"
            
        # Install TTS
        packages = [
            "TTS>=0.22.0",
            "torch>=1.13.0",
            "torchaudio>=0.13.0",
            "flask>=2.0.0",
            "flask-cors>=4.0.0",
            "numpy>=1.21.0",
            "scipy>=1.7.0",
            "librosa>=0.9.0",
            "soundfile>=0.12.0"
        ]
        
        for package in packages:
            self.log(f"Installing {package}...")
            if not self.run_command(f"{pip_cmd} install {package}"):
                self.log(f"Failed to install {package}", "ERROR")
                return False
                
        self.log("Coqui TTS installed successfully ✓")
        return True
        
    def download_female_voice_models(self):
        """Download pre-trained female voice models"""
        self.log("Downloading female voice models...")
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Models to download
        models = {
            "jenny": {
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "vocoder": "vocoder_models/en/ljspeech/hifigan_v2",
                "description": "Sweet female voice (Jenny)"
            },
            "aria": {
                "model": "tts_models/en/vctk/vits",
                "speaker": "p225",  # Female speaker
                "description": "Gentle female voice (Aria)"
            },
            "maya": {
                "model": "tts_models/en/ljspeech/glow-tts",
                "vocoder": "vocoder_models/en/ljspeech/hifigan_v2",
                "description": "Professional female voice (Maya)"
            }
        }
        
        if os.name == 'nt':  # Windows
            python_cmd = f"{self.tts_dir}/venv/Scripts/python"
        else:  # Unix/Linux/Mac
            python_cmd = f"{self.tts_dir}/venv/bin/python"
            
        for voice_name, config in models.items():
            self.log(f"Downloading {voice_name} model...")
            
            # Download main model
            download_cmd = f"{python_cmd} -c \"from TTS.api import TTS; TTS('{config['model']}', progress_bar=True)\""
            if not self.run_command(download_cmd):
                self.log(f"Failed to download {voice_name} model", "WARNING")
                continue
                
            # Download vocoder if specified
            if 'vocoder' in config:
                vocoder_cmd = f"{python_cmd} -c \"from TTS.api import TTS; TTS('{config['vocoder']}', progress_bar=True)\""
                if not self.run_command(vocoder_cmd):
                    self.log(f"Failed to download {voice_name} vocoder", "WARNING")
                    
        self.log("Female voice models downloaded ✓")
        return True
        
    def create_tts_server(self):
        """Create Flask TTS server"""
        self.log("Creating TTS server...")
        
        server_code = '''#!/usr/bin/env python3
"""
Female Voice TTS Server for MyDoc AI
Provides sweet female voices using Coqui TTS
"""

import os
import io
import json
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from TTS.api import TTS
import torch
import numpy as np
import soundfile as sf
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class FemaleVoiceTTSServer:
    def __init__(self):
        self.models = {}
        self.load_models()
        
    def load_models(self):
        """Load pre-trained female voice models"""
        logger.info("Loading female voice models...")
        
        try:
            # Jenny - Sweet medical assistant voice
            self.models['jenny'] = {
                'tts': TTS("tts_models/en/ljspeech/tacotron2-DDC"),
                'vocoder': "vocoder_models/en/ljspeech/hifigan_v2",
                'description': 'Sweet, caring female voice perfect for medical consultations',
                'characteristics': ['warm', 'caring', 'professional', 'clear']
            }
            logger.info("✓ Jenny voice model loaded")
            
            # Aria - Gentle healthcare voice  
            self.models['aria'] = {
                'tts': TTS("tts_models/en/vctk/vits"),
                'speaker': 'p225',  # Female speaker
                'description': 'Soft, reassuring voice for health guidance',
                'characteristics': ['gentle', 'reassuring', 'empathetic']
            }
            logger.info("✓ Aria voice model loaded")
            
            # Maya - Smart medical AI
            self.models['maya'] = {
                'tts': TTS("tts_models/en/ljspeech/glow-tts"),
                'vocoder': "vocoder_models/en/ljspeech/hifigan_v2", 
                'description': 'Intelligent, friendly voice for medical AI',
                'characteristics': ['intelligent', 'friendly', 'trustworthy']
            }
            logger.info("✓ Maya voice model loaded")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            
    def synthesize_speech(self, text, voice_model='jenny', speed=1.0, pitch=1.0):
        """Synthesize speech with specified voice"""
        try:
            if voice_model not in self.models:
                voice_model = 'jenny'  # Default fallback
                
            model_config = self.models[voice_model]
            tts = model_config['tts']
            
            # Process text for better female voice delivery
            processed_text = self.process_text_for_female_voice(text)
            
            # Generate speech
            if 'speaker' in model_config:
                # Multi-speaker model
                wav = tts.tts(text=processed_text, speaker=model_config['speaker'])
            else:
                # Single speaker model
                wav = tts.tts(text=processed_text)
                
            # Apply speed and pitch modifications
            if speed != 1.0 or pitch != 1.0:
                wav = self.modify_audio(wav, speed, pitch)
                
            return wav, tts.synthesizer.output_sample_rate
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None, None
            
    def process_text_for_female_voice(self, text):
        """Process text for better female voice delivery"""
        # Add caring expressions for medical context
        caring_phrases = {
            'Hello': 'Hello there',
            'Hi': 'Hi there', 
            'I understand': 'I completely understand',
            'That sounds': 'That sounds concerning',
            'You should': 'I would recommend that you',
            'Take care': 'Please take good care of yourself'
        }
        
        processed_text = text
        for original, caring in caring_phrases.items():
            processed_text = processed_text.replace(original, caring)
            
        # Add gentle pauses
        processed_text = processed_text.replace('. ', '. ... ')
        processed_text = processed_text.replace('? ', '? ... ')
        processed_text = processed_text.replace('! ', '! ... ')
        
        return processed_text
        
    def modify_audio(self, wav, speed=1.0, pitch=1.0):
        """Modify audio speed and pitch"""
        try:
            import librosa
            
            # Convert to numpy array if needed
            if torch.is_tensor(wav):
                wav = wav.cpu().numpy()
                
            # Modify speed (time stretching)
            if speed != 1.0:
                wav = librosa.effects.time_stretch(wav, rate=speed)
                
            # Modify pitch (pitch shifting)
            if pitch != 1.0:
                # Convert pitch ratio to semitones
                semitones = 12 * np.log2(pitch)
                wav = librosa.effects.pitch_shift(wav, sr=22050, n_steps=semitones)
                
            return wav
            
        except Exception as e:
            logger.warning(f"Audio modification failed: {e}")
            return wav

# Initialize TTS server
tts_server = FemaleVoiceTTSServer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': len(tts_server.models),
        'available_voices': list(tts_server.models.keys())
    })

@app.route('/api/tts', methods=['POST'])
def synthesize_text():
    """Main TTS endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
            
        text = data['text']
        voice_model = data.get('model_name', 'jenny')
        speed = data.get('speed', 1.0)
        pitch = data.get('pitch', 1.0)
        
        # Validate parameters
        speed = max(0.5, min(2.0, float(speed)))
        pitch = max(0.5, min(2.0, float(pitch)))
        
        logger.info(f"Synthesizing: '{text[:50]}...' with {voice_model} voice")
        
        # Generate speech
        wav, sample_rate = tts_server.synthesize_speech(text, voice_model, speed, pitch)
        
        if wav is None:
            return jsonify({'error': 'Speech synthesis failed'}), 500
            
        # Convert to audio file
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wav, sample_rate, format='WAV')
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='speech.wav'
        )
        
    except Exception as e:
        logger.error(f"TTS request failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voices', methods=['GET'])
def get_available_voices():
    """Get available voice models"""
    voices = []
    for voice_id, config in tts_server.models.items():
        voices.append({
            'id': voice_id,
            'name': voice_id.title(),
            'description': config['description'],
            'characteristics': config['characteristics']
        })
    
    return jsonify({'voices': voices})

@app.route('/api/test', methods=['POST'])
def test_voice():
    """Test voice synthesis"""
    try:
        data = request.get_json()
        voice_model = data.get('voice', 'jenny')
        
        test_text = "Hello! I'm your AI medical assistant. I'm here to help you with your health questions in a caring and professional manner."
        
        wav, sample_rate = tts_server.synthesize_speech(test_text, voice_model)
        
        if wav is None:
            return jsonify({'error': 'Voice test failed'}), 500
            
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wav, sample_rate, format='WAV')
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='test.wav'
        )
        
    except Exception as e:
        logger.error(f"Voice test failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🎤 Starting Female Voice TTS Server...")
    logger.info(f"Available voices: {list(tts_server.models.keys())}")
    app.run(host='0.0.0.0', port=5002, debug=False)
'''
        
        server_file = self.tts_dir / "tts_server.py"
        server_file.write_text(server_code)
        
        # Make executable
        if os.name != 'nt':
            os.chmod(server_file, 0o755)
            
        self.log("TTS server created ✓")
        return True
        
    def create_startup_scripts(self):
        """Create startup scripts for the TTS server"""
        self.log("Creating startup scripts...")
        
        # Windows batch script
        windows_script = f'''@echo off
echo Starting Female Voice TTS Server...
cd /d "{self.tts_dir}"
venv\\Scripts\\python tts_server.py
pause
'''
        
        (self.tts_dir / "start_tts_server.bat").write_text(windows_script)
        
        # Unix shell script
        unix_script = f'''#!/bin/bash
echo "Starting Female Voice TTS Server..."
cd "{self.tts_dir}"
source venv/bin/activate
python tts_server.py
'''
        
        unix_file = self.tts_dir / "start_tts_server.sh"
        unix_file.write_text(unix_script)
        os.chmod(unix_file, 0o755)
        
        self.log("Startup scripts created ✓")
        return True
        
    def create_config_file(self):
        """Create configuration file"""
        config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5002,
                "debug": False
            },
            "voices": {
                "default": "jenny",
                "available": ["jenny", "aria", "maya"]
            },
            "audio": {
                "sample_rate": 22050,
                "format": "wav"
            },
            "limits": {
                "max_text_length": 1000,
                "rate_limit": 60
            }
        }
        
        config_file = self.tts_dir / "config.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        self.log("Configuration file created ✓")
        return True
        
    def setup(self):
        """Main setup process"""
        self.log("🎤 Setting up Female Voice TTS Server...")
        
        try:
            # Check prerequisites
            if not self.check_python_version():
                return False
                
            # Create directories
            self.tts_dir.mkdir(exist_ok=True)
            
            # Install Coqui TTS
            if not self.install_coqui_tts():
                return False
                
            # Download models
            if not self.download_female_voice_models():
                return False
                
            # Create server
            if not self.create_tts_server():
                return False
                
            # Create startup scripts
            if not self.create_startup_scripts():
                return False
                
            # Create config
            if not self.create_config_file():
                return False
                
            self.log("🎉 Female Voice TTS Server setup completed successfully!")
            self.log("")
            self.log("To start the server:")
            if os.name == 'nt':
                self.log(f"  Windows: {self.tts_dir}/start_tts_server.bat")
            else:
                self.log(f"  Unix/Linux/Mac: {self.tts_dir}/start_tts_server.sh")
            self.log("")
            self.log("Server will be available at: http://localhost:5002")
            self.log("Test endpoint: http://localhost:5002/health")
            
            return True
            
        except Exception as e:
            self.log(f"Setup failed: {e}", "ERROR")
            return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python setup_female_voice_server.py")
        print("Sets up Coqui TTS server with sweet female voices for MyDoc AI")
        return
        
    setup = FemaleVoiceServerSetup()
    success = setup.setup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()