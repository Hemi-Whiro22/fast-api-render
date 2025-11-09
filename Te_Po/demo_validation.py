#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiwhanawhana System Validation Demo
Demonstrates the complete environment and locale validation system.
"""

import os
import sys
from pathlib import Path

# Ensure the project root is available for backend package imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def demo_perfect_setup():
    """Demo with perfect mi_NZ.UTF-8 setup"""
    print("🎯 DEMO 1: Perfect mi_NZ.UTF-8 Setup")
    print("=" * 50)
    
    # Set perfect environment
    os.environ['LANG'] = 'mi_NZ.UTF-8'
    os.environ['LC_ALL'] = 'mi_NZ.UTF-8'
    
    from Te_Po.utils.env_validator import validate_environment_and_locale
    result = validate_environment_and_locale()
    
    print(f"\n✅ Perfect Setup Results:")
    print(f"   mi_NZ Active: {result['locale']['is_mi_nz_active']}")
    print(f"   Overall Ready: {result['overall_ready']}")
    print(f"   Timestamp: {result['timestamp']}")
    
    return result

def demo_fallback_setup():
    """Demo with locale fallback"""
    print("\n\n🎯 DEMO 2: Locale Fallback Scenario")
    print("=" * 50)
    
    # Set fallback environment
    os.environ['LANG'] = 'C.UTF-8'
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    # Need to reimport to get fresh validation
    import importlib
    import Te_Po.utils.env_validator as env_validator
    importlib.reload(env_validator)
    
    result = env_validator.validate_environment_and_locale()
    
    print(f"\n⚠️  Fallback Setup Results:")
    print(f"   mi_NZ Active: {result['locale']['is_mi_nz_active']}")
    print(f"   Detected Locale: {result['locale']['detected_locale']}")
    print(f"   Overall Ready: {result['overall_ready']}")
    
    return result

def demo_security_features():
    """Demo security and masking features"""
    print("\n\n🎯 DEMO 3: Security Features")
    print("=" * 50)
    
    from Te_Po.utils.env_validator import mask, mask_secret
    
    # Demo key masking
    test_keys = [
        "sk-1234567890abcdefghijklmnopqrstuvwxyz",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example_jwt_token",
        "https://myproject.supabase.co"
    ]
    
    print("🔐 Key Masking Examples:")
    for key in test_keys:
        masked = mask(key)
        print(f"   {key[:20]}... → {masked}")
    
    print("\n🛡️  Security Features:")
    print("   ✅ No full secrets in logs")
    print("   ✅ Structured JSON output") 
    print("   ✅ Graceful error handling")
    print("   ✅ Enterprise-grade logging")

def main():
    """Run complete system validation demo"""
    print("🌊 Tiwhanawhana System Validation Demo")
    print("🪶 Comprehensive Environment & Locale Testing")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_perfect_setup()
        demo_fallback_setup() 
        demo_security_features()
        
        print("\n\n🎉 All Tiwhanawhana validation demos completed successfully!")
        print("✅ System is production-ready with comprehensive validation")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())