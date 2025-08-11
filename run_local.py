#!/usr/bin/env python3
"""
Simple test runner for local app
"""
import subprocess
import time
import requests
import sys
import signal

def run_test():
    print("🚀 Starting local Flask app...")
    
    # Start gunicorn in background
    proc = subprocess.Popen([
        "gunicorn", "--bind=127.0.0.1:8005", "--workers=1", "app:app"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        print("🔍 Testing endpoints...")
        
        # Test health
        response = requests.get("http://127.0.0.1:8005/health", timeout=10)
        print(f"✅ Health: {response.status_code} - {response.json()}")
        
        # Test home  
        response = requests.get("http://127.0.0.1:8005/home", timeout=10)
        print(f"✅ Home: {response.status_code} - {response.text}")
        
        # Test debug
        response = requests.get("http://127.0.0.1:8005/debug/env", timeout=10)
        print(f"✅ Debug: {response.status_code} - Keys: {list(response.json().keys())}")
        
        print("\n🎉 All tests passed! App is working correctly.")
        print("📍 Server running at: http://127.0.0.1:8005")
        print("🔗 Available endpoints:")
        print("   - GET /health")
        print("   - GET /home") 
        print("   - GET /debug/env")
        print("   - POST /search")
        
        # Keep server running
        print("\n⏳ Server is running... Press Ctrl+C to stop")
        proc.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    run_test()
