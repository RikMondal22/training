#!/usr/bin/env python3
"""
Startup script to verify the BSK recommendation system is properly configured.
Run this script to diagnose any issues before starting the Streamlit application.
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "backend"))
sys.path.append(str(project_root / "ai_service"))

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    # Test basic dependencies
    try:
        import streamlit as st
        print("✅ Streamlit available")
    except ImportError as e:
        print(f"❌ Streamlit not available: {e}")
    
    try:
        import pandas as pd
        import numpy as np
        from sklearn.cluster import KMeans
        print("✅ Data science libraries available")
    except ImportError as e:
        print(f"❌ Data science libraries missing: {e}")
    
    # Test AI service imports
    try:
        from ai_service.service_recommendation import recommend_bsk_for_service_from_db, initialize_embeddings_from_db
        print("✅ AI service functions available")
        return True
    except ImportError as e:
        print(f"⚠️ AI service functions not available: {e}")
        try:
            from ai_service.service_recommendation import recommend_bsk_for_service
            print("✅ Basic AI service functions available (fallback mode)")
            return True
        except ImportError as e2:
            print(f"❌ No AI service functions available: {e2}")
            return False

def test_database():
    """Test database connectivity."""
    print("\n🔍 Testing database connectivity...")
    
    try:
        from ai_service.database_service import get_database_session, fetch_services_from_db
        
        # Test session creation
        db = get_database_session()
        if db:
            print("✅ Database session created successfully")
            db.close()
            
            # Test data fetching
            services_df = fetch_services_from_db()
            if services_df is not None:
                print(f"✅ Services data fetched: {len(services_df)} records")
                return True
            else:
                print("⚠️ Could not fetch services data")
                return False
        else:
            print("❌ Could not create database session")
            return False
            
    except ImportError as e:
        print(f"❌ Database service not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_backend_api():
    """Test backend API connectivity."""
    print("\n🔍 Testing backend API...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:54300/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API accessible")
            
            # Test specific endpoints
            endpoints = ["/bsk/", "/services/", "/provisions/"]
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"http://localhost:54300{endpoint}?limit=1", timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        print(f"✅ {endpoint} endpoint: {len(data)} records available")
                    else:
                        print(f"⚠️ {endpoint} endpoint returned status {resp.status_code}")
                except Exception as e:
                    print(f"❌ {endpoint} endpoint failed: {e}")
            
            return True
        else:
            print(f"⚠️ Backend API returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend API not accessible - is the backend server running?")
        print("   Start with: cd backend && python -m uvicorn app.main:app --reload --port 54300")
        return False
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def test_ai_models():
    """Test AI model loading."""
    print("\n🔍 Testing AI models...")
    
    try:
        from ai_service.service_recommendation import get_model
        
        model = get_model()
        if model:
            print("✅ AI model loaded successfully")
            
            # Test embedding
            test_text = "Digital service application"
            embedding = model.encode([test_text])
            print(f"✅ Embedding generation works: {embedding.shape}")
            return True
        else:
            print("❌ Could not load AI model")
            return False
            
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        return False

def test_embeddings():
    """Test embedding initialization."""
    print("\n🔍 Testing embeddings...")
    
    try:
        from ai_service.service_recommendation import initialize_embeddings_from_db
        
        success = initialize_embeddings_from_db(force_rebuild=False)
        if success:
            print("✅ Embeddings initialized successfully")
            return True
        else:
            print("⚠️ Embeddings initialization incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 BSK Recommendation System Diagnostic")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Backend API", test_backend_api),
        ("AI Models", test_ai_models),
        ("Embeddings", test_embeddings)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 Recommendations:")
    if all_passed:
        print("✅ All tests passed! The system should work correctly.")
        print("📝 You can now run: streamlit run frontend/pages/05_Service_Recommendation.py")
    else:
        print("⚠️ Some tests failed. Please address the issues above.")
        
        if not results.get("Backend API", False):
            print("   → Start the backend: cd backend && python -m uvicorn app.main:app --reload --port 54300")
        
        if not results.get("Database", False):
            print("   → Check database configuration and connectivity")
        
        if not results.get("AI Models", False):
            print("   → Install AI dependencies: pip install sentence-transformers torch")
        
        if not results.get("Embeddings", False):
            print("   → Install ChromaDB: pip install chromadb")

if __name__ == "__main__":
    main()
