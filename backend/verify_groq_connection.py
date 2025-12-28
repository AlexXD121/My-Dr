
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

try:
    from groq import Groq
except ImportError:
    print("❌ 'groq' library not found. Please install it: pip install groq")
    sys.exit(1)

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables.")
        return

    print(f"🔑 Found API Key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        client = Groq(api_key=api_key)
        
        print("🤖 Testing connection to Groq API (llama3-70b-8192)...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Groq connection successful!' if you can hear me."}
            ],
            temperature=0.5,
            max_tokens=50
        )
        
        reply = completion.choices[0].message.content
        print(f"✅ Response: {reply}")
        print("🎉 Verification Successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_groq()
