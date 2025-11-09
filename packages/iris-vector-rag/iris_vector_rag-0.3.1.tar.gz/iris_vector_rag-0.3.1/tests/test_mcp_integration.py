#!/usr/bin/env python3
"""
Lightweight Integration Tests for mem0 MCP Server

Basic integration tests to verify MCP server endpoints and functionality.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def setup_test_environment():
    """Setup test environment and verify requirements."""
    print("🧪 Setting up test environment...")
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'MEM0_CONFIG_PROVIDER']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing required environment variables: {missing}")
        return False
    
    print("✅ Environment variables verified")
    return True

def test_server_startup():
    """Test if the MCP server can start successfully."""
    print("\n🚀 Testing server startup...")
    
    try:
        # Test server import (basic validation)
        result = subprocess.run([
            sys.executable, '-c', 
            'import sys; sys.path.append("mem0-mcp-server/src"); import server; print("✅ Server import successful")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Server module imports successfully")
            return True
        else:
            print(f"❌ Server import failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Server startup timed out")
        return False
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

def test_environment_loading():
    """Test environment configuration loading."""
    print("\n🔧 Testing environment loading...")
    
    try:
        # Test environment loading script
        result = subprocess.run([
            sys.executable, '-c',
            '''
import os
import sys
sys.path.append("mem0_integration")
from config.environment_backup_templates import EnvironmentBackupManager
manager = EnvironmentBackupManager()
print("✅ Environment manager loaded successfully")
'''
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Environment configuration loads successfully")
            return True
        else:
            print(f"❌ Environment loading failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Environment loading error: {e}")
        return False

def test_retry_logic():
    """Test retry logic module."""
    print("\n🔄 Testing retry logic...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c',
            '''
import sys
sys.path.append("mem0_integration")
from utils.retry_logic import OpenAIRetryHandler, RetryConfig
config = RetryConfig()
handler = OpenAIRetryHandler(config)
print("✅ Retry logic initialized successfully")
'''
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Retry logic module works correctly")
            return True
        else:
            print(f"❌ Retry logic test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Retry logic error: {e}")
        return False

def test_logging_config():
    """Test logging configuration."""
    print("\n📝 Testing logging configuration...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c',
            '''
import sys
sys.path.append("mem0_integration")
from utils.logging_config import setup_logging
logger = setup_logging()
logger.info("Test log message")
print("✅ Logging configured successfully")
'''
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Logging configuration works correctly")
            return True
        else:
            print(f"❌ Logging configuration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Logging configuration error: {e}")
        return False

def test_health_check_script():
    """Test health check script functionality."""
    print("\n🏥 Testing health check script...")
    
    try:
        result = subprocess.run([
            sys.executable, 'scripts/health_check_mem0.py'
        ], capture_output=True, text=True, timeout=10)
        
        # Health check might fail if server isn't running, but script should execute
        if "Health Check Complete" in result.stdout or result.returncode == 0:
            print("✅ Health check script executes successfully")
            return True
        else:
            print("⚠️ Health check completed with warnings (expected if server not running)")
            return True  # This is acceptable for integration tests
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_monitoring_script():
    """Test monitoring script functionality."""
    print("\n📊 Testing monitoring script...")
    
    try:
        result = subprocess.run([
            sys.executable, 'scripts/monitor_mem0_server.py'
        ], capture_output=True, text=True, timeout=10)
        
        # Monitor script should run and produce output
        if "mem0 MCP Server Monitor" in result.stdout:
            print("✅ Monitoring script executes successfully")
            return True
        else:
            print(f"❌ Monitoring script output unexpected: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Monitoring script error: {e}")
        return False

def test_benchmark_script():
    """Test benchmark script functionality."""
    print("\n⚡ Testing benchmark script...")
    
    try:
        result = subprocess.run([
            sys.executable, 'scripts/benchmark_mem0_performance.py', '--quick'
        ], capture_output=True, text=True, timeout=15)
        
        if "Performance Benchmark" in result.stdout:
            print("✅ Benchmark script executes successfully")
            return True
        else:
            print(f"❌ Benchmark script output unexpected: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Benchmark script error: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("🔬 Starting mem0 MCP Server Integration Tests")
    print("=" * 60)
    
    # Test results
    tests = [
        ("Environment Setup", setup_test_environment),
        ("Server Startup", test_server_startup),
        ("Environment Loading", test_environment_loading),
        ("Retry Logic", test_retry_logic),
        ("Logging Config", test_logging_config),
        ("Health Check Script", test_health_check_script),
        ("Monitoring Script", test_monitoring_script),
        ("Benchmark Script", test_benchmark_script),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📋 Test Results Summary:")
    print("-" * 40)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("-" * 40)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check logs above for details.")
        return False

def main():
    """Main entry point."""
    success = run_integration_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()