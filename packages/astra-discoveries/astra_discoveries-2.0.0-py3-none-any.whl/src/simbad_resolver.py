#!/usr/bin/env python3
"""
ASTRA: SIMBAD Name Resolver
Resolves transient IDs to coordinates for Gaia cross-matching
"""

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import pandas as pd
import time

class SimbadResolver:
    """Resolve transient names to coordinates using SIMBAD"""
    
    def __init__(self):
        # Configure SIMBAD query
        Simbad.add_votable_fields('otype')
        self.simbad = Simbad()
        
    def resolve_name(self, name):
        """Resolve a single name to coordinates"""
        try:
            # Clean up the name and try variations
            name_clean = name.strip()
            
            # Try different name formats
            names_to_try = [
                name_clean,
                name_clean.replace('AT', 'SN'),
                name_clean.replace('AT2025', 'AT 2025'),
                name_clean.replace('AT2025', 'SN 2025')
            ]
            
            for test_name in names_to_try:
                try:
                    result = self.simbad.query_object(test_name)
                    if result is not None and len(result) > 0:
                        # Extract coordinates (RA and DEC are always returned)
                        ra = result['RA'][0]
                        dec = result['DEC'][0]
                        obj_type = result['OTYPE'][0] if 'OTYPE' in result.keys() else None
                        
                        return {
                            'ra': ra,
                            'dec': dec,
                            'simbad_type': obj_type,
                            'simbad_match': True,
                            'simbad_query': test_name
                        }
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"   ✗ Failed to resolve {name}: {e}")
            return None
    
    def resolve_batch(self, names, batch_size=10, delay=1.0):
        """Resolve multiple names with rate limiting"""
        results = []
        
        print(f"🔭 Resolving {len(names)} names with SIMBAD...")
        
        for i, name in enumerate(names, 1):
            if i % batch_size == 0:
                print(f"   Progress: {i}/{len(names)}...")
                time.sleep(delay)  # Be nice to SIMBAD server
            
            result = self.resolve_name(name)
            if result:
                result['id'] = name
                results.append(result)
                query_name = result.get('simbad_query', name)
                print(f"   ✓ {name} → {query_name}: {result['ra']} {result['dec']}")
        
        df = pd.DataFrame(results)
        print(f"   📊 Successfully resolved {len(df)} objects")
        return df
    
    def add_coordinates_to_catalog(self, catalog):
        """Add coordinates to a catalog that doesn't have them"""
        if catalog.empty:
            return catalog
        
        # Find objects without coordinates
        if 'ra' in catalog.columns:
            missing_coords = catalog[catalog['ra'].isna()]['id'].tolist()
        else:
            missing_coords = catalog['id'].tolist()
        
        if not missing_coords:
            print("✓ All objects already have coordinates")
            return catalog
        
        print(f"🔍 Found {len(missing_coords)} objects without coordinates")
        
        # Resolve them
        resolved = self.resolve_batch(missing_coords)
        
        if resolved.empty:
            print("⚠️  No coordinates could be resolved")
            return catalog
        
        # Merge back into catalog
        if 'ra' in catalog.columns:
            # Update existing rows
            for idx, row in resolved.iterrows():
                mask = catalog['id'] == row['id']
                catalog.loc[mask, 'ra'] = row['ra']
                catalog.loc[mask, 'dec'] = row['dec']
                catalog.loc[mask, 'simbad_type'] = row['simbad_type']
        else:
            # Add new columns
            catalog = catalog.merge(resolved[['id', 'ra', 'dec', 'simbad_type']], 
                                   on='id', how='left')
        
        return catalog

def test_resolver():
    """Test with some known objects that should be in SIMBAD"""
    resolver = SimbadResolver()
    
    # Test with established objects (not brand new transients)
    test_names = [
        "V838 Mon",      # Known variable star
        "GK Per",        # Known nova
        "SN 1987A",      # Famous supernova
        "M 31"           # Andromeda Galaxy
    ]
    
    print("Testing SIMBAD resolver with known objects...")
    results = resolver.resolve_batch(test_names)
    
    if not results.empty:
        print("\n📊 Results:")
        print(results[['id', 'ra', 'dec', 'simbad_type']].to_string())
        
        # Save to CSV
        results.to_csv('simbad_test_resolved.csv', index=False)
        print("\n💾 Saved to simbad_test_resolved.csv")
    else:
        print("\n❌ No objects resolved")
    
    return results

if __name__ == "__main__":
    # Run test first
    test_results = test_resolver()
    
    print("\n" + "="*60)
    
    # Now try with transients (may not be in SIMBAD yet)
    resolver = SimbadResolver()
    
    # Load recent transients and try to resolve them
    try:
        import pandas as pd
        transients = pd.read_csv('bright_transients.csv')
        print(f"\nAttempting to resolve {len(transients)} recent transients...")
        print("(Note: Very recent transients may not be in SIMBAD yet)")
        
        resolved = resolver.resolve_batch(transients['id'].tolist()[:5])  # Try first 5
        
        if not resolved.empty:
            print("\n✓ Some transients were resolved!")
            resolved.to_csv('simbad_transients_resolved.csv', index=False)
        else:
            print("\nℹ️  No recent transients in SIMBAD yet (expected for new discoveries)")
            
    except FileNotFoundError:
        print("\nℹ️  bright_transients.csv not found, skipping transient resolution test")