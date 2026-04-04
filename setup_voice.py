#!/usr/bin/env python
"""
Voice Update Setup Script for Alumni Tracer
This script helps you configure OpenAI API for voice processing.
"""

import os
from pathlib import Path

def setup_voice_api():
    """Guide user through OpenAI API setup"""

    print("🎤 Alumni Tracer - Voice Update Setup")
    print("=" * 40)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found. Creating one...")
        env_file.write_text("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ Created .env file")

    # Check current API key
    current_key = os.getenv('OPENAI_API_KEY', '')
    if current_key and current_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key is already configured")
        return

    print("\n📋 To set up voice processing:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the API key")
    print("4. Add it to your .env file as: OPENAI_API_KEY=your_key_here")

    api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()

    if api_key:
        # Update .env file
        env_content = env_file.read_text()
        if 'OPENAI_API_KEY=' in env_content:
            env_content = env_content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={api_key}')
        else:
            env_content += f"\nOPENAI_API_KEY={api_key}"

        env_file.write_text(env_content)
        print("✅ API key saved to .env file")
    else:
        print("⚠️  No API key provided. Voice processing will use fallback mode.")

    print("\n🎯 Testing voice processing...")
    print("Run: python manage.py runserver")
    print("Then visit: /account/employment/add/ and try the voice recorder!")

if __name__ == "__main__":
    setup_voice_api()