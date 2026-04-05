import requests
import base64
import os

def test_stt():
    print("Testing STT (/api/stt)...")
    # Small dummy wav file (1 second of silence)
    dummy_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    audio_b64 = base64.b64encode(dummy_wav).decode('utf-8')
    
    try:
        response = requests.post('http://localhost:5001/api/stt', json={'audio': audio_b64})
        if response.status_code == 200:
            print("✅ STT Success!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ STT Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"💥 STT Exception: {e}")

def test_multimodal_chat():
    print("\nTesting Multimodal Chat (/api/chat/multimodal)...")
    # Small dummy text file
    dummy_txt = b"Bismillahi Rahmani Rahim. This is a test for the Islamic AI Agent."
    file_b64 = base64.b64encode(dummy_txt).decode('utf-8')
    
    try:
        response = requests.post('http://localhost:5001/api/chat/multimodal', json={
            'message': 'What is in this document?',
            'file': file_b64,
            'mime_type': 'text/plain',
            'user_gender': 'not_specified'
        })
        if response.status_code == 200:
            print("✅ Multimodal Chat Success!")
            print(f"Response: {response.json().get('response')[:100]}...")
        else:
            print(f"❌ Multimodal Chat Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"💥 Multimodal Chat Exception: {e}")

if __name__ == "__main__":
    test_stt()
    test_multimodal_chat()
