#!/usr/bin/env python3
"""
ASTRA Infrastructure Test Suite
Tests that the core ASTRA system is properly installed and functional
"""

import sys
import os

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing core imports...")
    
    try:
        import astroquery
        print(f"✅ astroquery {astroquery.__version__}")
    except ImportError as e:
        print(f"❌ astroquery: {e}")
        return False
    
    try:
        import astropy
        print(f"✅ astropy {astropy.__version__}")
    except ImportError as e:
        print(f"❌ astropy: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ numpy {numpy.__version__}")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    try:
        import pandas
        print(f"✅ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print(f"✅ beautifulsoup4")
    except ImportError as e:
        print(f"❌ beautifulsoup4: {e}")
        return False
    
    return True

def test_astra_imports():
    """Test that ASTRA modules can be imported."""
    print("\nTesting ASTRA module imports...")
    
    try:
        from src import run_basic_discovery, run_advanced_discovery, system_check
        print("✅ ASTRA core functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ ASTRA modules: {e}")
        return False

def test_web_access():
    """Test that we can access public data sources."""
    print("\nTesting web access to data sources...")
    
    import requests
    
    sources = [
        ("Rochester Supernova Page", "http://www.rochesterastronomy.org/supernova.html"),
    ]
    
    all_good = True
    for name, url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} accessible")
            else:
                print(f"⚠️  {name} returned status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_good = False
    
    return all_good

def test_system_check():
    """Test the system check function."""
    print("\nTesting system check function...")
    
    try:
        from src import system_check
        result = system_check()
        if result:
            print("✅ System check passed")
            return True
        else:
            print("❌ System check failed")
            return False
    except Exception as e:
        print(f"❌ System check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_discovery_pipeline():
    """Test a minimal discovery pipeline."""
    print("\nTesting minimal discovery pipeline...")
    
    try:
        from src import run_basic_discovery
        
        # Run a quick discovery (basic mode for speed)
        results = run_basic_discovery()
        
        if results and 'transients' in results:
            transients = results['transients']
            print(f"✅ Discovery pipeline returned results")
            print(f"   Transients shape: {transients.shape}")
            print(f"   Columns: {list(transients.columns)}")
            return True
        else:
            print("❌ Discovery pipeline returned no results")
            return False
    except Exception as e:
        print(f"❌ Discovery pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all infrastructure tests."""
    print("=" * 60)
    print("ASTRA INFRASTRUCTURE TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_astra_imports,
        test_web_access,
        test_system_check,
        test_discovery_pipeline
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print()
        print("🎉 ASTRA IS READY FOR DISCOVERY OPS")
        print()
        print("Next steps:")
        print("  1. Run: ./scripts/run_advanced.sh")
        print("  2. View: cat advanced_report")
        print("  3. Schedule: Add to crontab")
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Check output above.")
        print()
        print("Common issues:")
        print("  • Virtual environment not activated")
        print("  • Missing dependencies (pip install -r requirements.txt)")
        print("  • Internet connection issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())