"""
ASTRA: Autonomous System for Transient Research & Analysis

A fully autonomous astronomical transient discovery engine that identifies
scientifically interesting supernovae, cataclysmic variables, and rare stellar
phenomena using publicly available data sources without requiring proprietary
API access.

Main Modules:
-------------
transient_scraper : Data collection from public sources
astra_discovery_engine : Basic anomaly detection
enhanced_discovery_v2 : Advanced multi-factor scoring

Usage:
------
>>> from astra import run_basic_discovery, run_advanced_discovery
>>> results = run_advanced_discovery()
>>> print(f"Found {len(results['anomalies'])} anomalies")
"""

__version__ = "1.0.0"
__author__ = "ASTRA Collaboration"
__email__ = "astra@shannonlabs.io"

from .transient_scraper import TransientScraper, get_recent_transients
from .astra_discovery_engine import AstraDiscoveryEngine
from .enhanced_discovery_v2 import EnhancedDiscoveryEngineV2

__all__ = ['TransientScraper', 'AstraDiscoveryEngine', 'EnhancedDiscoveryEngineV2', 
           'get_recent_transients', 'run_basic_discovery', 'run_advanced_discovery']


def run_basic_discovery():
    """
    Run a basic ASTRA discovery cycle.
    
    Returns
    -------
    results : dict
        Dictionary containing transients and anomalies found.
    """
    engine = AstraDiscoveryEngine()
    return engine.run_discovery_pipeline()


def run_advanced_discovery():
    """
    Run an advanced ASTRA discovery cycle with enhanced scoring.
    
    Returns
    -------
    results : dict
        Dictionary containing transients and anomalies found.
    """
    engine = EnhancedDiscoveryEngineV2()
    return engine.run_advanced_pipeline()


def system_check():
    """Verify ASTRA infrastructure is ready."""
    try:
        import astroquery
        import astropy
        import numpy
        import pandas
        print("✅ ASTRA IS READY FOR DISCOVERY OPS")
        print(f"   astroquery {astroquery.__version__}")
        print(f"   astropy {astropy.__version__}")
        print(f"   numpy {numpy.__version__}")
        print(f"   pandas {pandas.__version__}")
        return True
    except ImportError as e:
        print(f"❌ ASTRA NOT READY: {e}")
        return False


if __name__ == "__main__":
    system_check()