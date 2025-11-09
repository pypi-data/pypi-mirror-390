#!/usr/bin/env python3
"""
ASTRA: Autonomous System for Theoretical & Research Astronomy
TNS-LESS Discovery Engine v1.1 (Fixed)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from datetime import datetime, timedelta
import re

class AstraDiscoveryEngine:
    """Main discovery engine for autonomous transient analysis"""
    
    def __init__(self):
        self.transients = pd.DataFrame()
        self.anomalies = []
        
    def scrape_rochester_page(self):
        """Scrape the Rochester Supernova page for recent transients"""
        print("🌐 Scraping Rochester Astronomy Supernova page...")
        
        url = "http://www.rochesterastronomy.org/supernova.html"
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"   Found {len(tables)} tables")
        
        transients = []
        
        # Look for tables with transient data
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            # Check if this looks like a transient table
            first_row = rows[0].get_text()
            if 'Name' in first_row and 'Mag' in first_row:
                print(f"   ✓ Table {i} looks like transient data ({len(rows)} rows)")
                
                # Parse data rows
                for row in rows[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) < 3:
                        continue
                    
                    try:
                        # Extract data
                        name = cols[0].get_text(strip=True) if len(cols) > 0 else ''
                        mag_str = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                        obj_type = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                        
                        # Clean magnitude
                        mag = None
                        if mag_str and mag_str != '-':
                            mag_match = re.search(r'([\d\.]+)', mag_str)
                            if mag_match:
                                mag = float(mag_match.group(1))
                        
                        # Only keep if it looks like a transient
                        if name and name.startswith(('AT', 'SN')):
                            transients.append({
                                'id': name,
                                'mag': mag,
                                'type': obj_type,
                                'source': f'Rochester_Table_{i}'
                            })
                    except Exception as e:
                        continue
        
        # Also try to find individual transient entries in the page
        text = soup.get_text()
        
        # Pattern for individual transient entries
        pattern = r'(AT\d{4}[\w]+)\s*=.*?\s+discovered\s+(\d{4}/\d{2}/\d{2})'
        matches = re.findall(pattern, text)
        
        if matches:
            print(f"   ✓ Found {len(matches)} individual transient entries")
            
            for match in matches[:100]:  # Limit to first 100 to avoid duplicates
                transient_id, date = match
                
                # Find more details around this match
                idx = text.find(transient_id)
                context = text[idx-200:idx+400]
                
                # Extract magnitude
                mag_match = re.search(r'Mag\s+([\d\.]+)', context)
                mag = float(mag_match.group(1)) if mag_match else None
                
                # Extract type
                type_match = re.search(r'Type\s+([\w\?]+)', context)
                obj_type = type_match.group(1) if type_match else 'unknown'
                
                # Extract RA/Dec
                ra_match = re.search(r'R\.A\.\s*=\s*([\dhms\.]+)', context)
                dec_match = re.search(r'Decl\.\s*=\s*([\+\-\d\s\.]+)', context)
                ra = ra_match.group(1) if ra_match else None
                dec = dec_match.group(1) if dec_match else None
                
                transients.append({
                    'id': transient_id,
                    'date': date,
                    'mag': mag,
                    'type': obj_type,
                    'ra': ra,
                    'dec': dec,
                    'source': 'Rochester_Entries'
                })
        
        df = pd.DataFrame(transients)
        print(f"   📊 Total transients collected: {len(df)}")
        
        if not df.empty:
            # Remove duplicates, keeping the one with most info
            df = df.sort_values('source', key=lambda x: x.map({'Rochester_Entries': 1, 'Rochester_Table_1': 0}))
            df = df.drop_duplicates('id', keep='first')
            
            print(f"   📊 After deduplication: {len(df)} transients")
            
            mag_min = df['mag'].min() if df['mag'].notna().any() else 'N/A'
            mag_max = df['mag'].max() if df['mag'].notna().any() else 'N/A'
            print(f"   📈 Magnitude range: {mag_min} - {mag_max}")
            
            type_counts = df['type'].value_counts().head()
            print(f"   🔭 Types found: {type_counts.to_dict()}")
            
            # Show coordinate availability
            has_coords = df['ra'].notna().sum() if 'ra' in df.columns else 0
            print(f"   📍 Coordinates available for: {has_coords} objects")
        
        return df
    
    def cross_match_with_gaia(self, transients, radius=5.0):
        """Cross-match transients with Gaia DR3 for proper motion/distance"""
        # Only cross-match if we have coordinates
        if 'ra' not in transients.columns:
            print("   ⚠️  No RA/Dec columns found, skipping Gaia cross-match")
            return pd.DataFrame()
        
        has_coords = transients[transients['ra'].notna() & transients['dec'].notna()]
        
        if has_coords.empty:
            print("   ⚠️  No valid coordinates, skipping Gaia cross-match")
            return pd.DataFrame()
        
        print(f"🔭 Cross-matching {len(has_coords)} objects with Gaia DR3...")
        
        from astroquery.gaia import Gaia
        
        results = []
        
        for idx, row in has_coords.iterrows():
            try:
                # Parse coordinates
                coord = SkyCoord(row['ra'], row['dec'], unit=(u.hourangle, u.deg))
                
                # Query Gaia
                job = Gaia.cone_search_async(coord, radius * u.arcsec)
                gaia_results = job.get_results()
                
                if len(gaia_results) > 0:
                    # Found Gaia match
                    star = gaia_results[0]
                    results.append({
                        'id': row['id'],
                        'gaia_match': True,
                        'gaia_dist_arcsec': float(coord.separation(
                            SkyCoord(star['ra'], star['dec'], unit=u.deg)
                        ).arcsec),
                        'pmra': float(star['pmra']) if 'pmra' in star.keys() else None,
                        'pmdec': float(star['pmdec']) if 'pmdec' in star.keys() else None,
                        'parallax': float(star['parallax']) if 'parallax' in star.keys() else None,
                        'g_mag': float(star['phot_g_mean_mag']) if 'phot_g_mean_mag' in star.keys() else None
                    })
                    print(f"   ✓ {row['id']}: Gaia match found (G={results[-1]['g_mag']:.1f})")
                else:
                    results.append({
                        'id': row['id'],
                        'gaia_match': False
                    })
                    
            except Exception as e:
                print(f"   ✗ {row['id']}: Error - {e}")
                results.append({
                    'id': row['id'],
                    'gaia_match': False,
                    'error': str(e)
                })
        
        return pd.DataFrame(results)
    
    def calculate_anomaly_score(self, row):
        """Calculate anomaly score based on multiple factors"""
        score = 0.0
        reasons = []
        
        # Brightness anomaly (very bright or very faint)
        if pd.notna(row['mag']):
            if row['mag'] < 16.0:
                score += 3.0
                reasons.append(f"Very bright (m={row['mag']:.1f})")
            elif row['mag'] > 20.0:
                score += 2.0
                reasons.append(f"Very faint (m={row['mag']:.1f})")
        
        # Unknown type
        if row['type'] == 'unknown' or row['type'] == 'unk':
            score += 2.0
            reasons.append("Unknown classification")
        
        # Type CV with unusual brightness
        if 'CV' in row['type'] and pd.notna(row['mag']):
            if row['mag'] < 16.0:
                score += 4.0
                reasons.append("CV at unusual brightness")
        
        # High proper motion from Gaia
        if 'pmra' in row and pd.notna(row['pmra']):
            pm = np.sqrt(row['pmra']**2 + row.get('pmdec', 0)**2)
            if pm > 50:  # mas/yr
                score += 3.0
                reasons.append(f"High proper motion ({pm:.0f} mas/yr)")
        
        # Parallax indicates nearby object
        if 'parallax' in row and pd.notna(row['parallax']):
            if row['parallax'] > 5:  # within 200 pc
                score += 2.0
                reasons.append(f"Nearby (π={row['parallax']:.1f} mas)")
        
        return score, reasons
    
    def find_anomalies(self, transients):
        """Identify anomalous transients"""
        print("🔍 Finding anomalies...")
        
        anomalies = []
        
        for idx, row in transients.iterrows():
            score, reasons = self.calculate_anomaly_score(row)
            
            if score >= 5.0:  # Threshold for interesting object
                anomalies.append({
                    'id': row['id'],
                    'mag': row['mag'],
                    'type': row['type'],
                    'score': score,
                    'reasons': reasons,
                    **{k: v for k, v in row.items() if k not in ['id', 'mag', 'type']}
                })
        
        # Sort by score
        anomalies = sorted(anomalies, key=lambda x: x['score'], reverse=True)
        
        print(f"   🎯 Found {len(anomalies)} anomalous objects")
        for i, anomaly in enumerate(anomalies[:5], 1):
            print(f"   {i}. {anomaly['id']} (score={anomaly['score']:.1f}) - {', '.join(anomaly['reasons'])}")
        
        return anomalies
    
    def generate_discovery_report(self, anomalies):
        """Generate formatted discovery report"""
        report = []
        report.append("=" * 80)
        report.append("ASTRA DISCOVERY REPORT - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append("=" * 80)
        report.append("")
        
        if not anomalies:
            report.append("No anomalies found in current dataset.")
            return "\n".join(report)
        
        report.append(f"🎯 HIGH-PRIORITY ANOMALIES ({len(anomalies)} found)")
        report.append("")
        
        for i, obj in enumerate(anomalies, 1):
            report.append(f"{i}. {obj['id']}")
            report.append(f"   Magnitude: {obj['mag']:.1f}" if pd.notna(obj['mag']) else "   Magnitude: Unknown")
            report.append(f"   Type: {obj['type']}")
            report.append(f"   Anomaly Score: {obj['score']:.1f}/10.0")
            report.append(f"   Reasons: {', '.join(obj['reasons'])}")
            
            if 'ra' in obj and obj['ra']:
                report.append(f"   Position: {obj['ra']} {obj.get('dec', '')}")
            
            if 'gaia_match' in obj:
                if obj['gaia_match']:
                    report.append(f"   Gaia: Match found (G={obj.get('g_mag', 'N/A'):.1f})")
                    if pd.notna(obj.get('parallax')):
                        dist = 1.0 / obj['parallax'] * 1000 if obj['parallax'] > 0 else None
                        if dist:
                            report.append(f"   Distance: ~{dist:.0f} pc")
                else:
                    report.append(f"   Gaia: No match within 5 arcsec")
            
            report.append("")
        
        return "\n".join(report)
    
    def run_discovery_pipeline(self, days=7):
        """Run the complete discovery pipeline"""
        print("🚀 ASTRA Discovery Pipeline Starting...")
        print("=" * 60)
        
        # Phase 1: Collect data
        transients = self.scrape_rochester_page()
        
        if transients.empty:
            print("❌ No transients found. Aborting.")
            return None
        
        # Phase 2: Cross-match with catalogs (only if we have coords)
        if 'ra' in transients.columns and transients['ra'].notna().any():
            gaia_results = self.cross_match_with_gaia(transients)
            # Merge results
            if not gaia_results.empty:
                transients = transients.merge(gaia_results, on='id', how='left')
        else:
            print("   ⚠️  Skipping Gaia cross-match (no coordinates)")
        
        # Phase 3: Find anomalies
        anomalies = self.find_anomalies(transients)
        
        # Phase 4: Generate report
        report = self.generate_discovery_report(anomalies)
        
        print("=" * 60)
        print("✅ Discovery pipeline complete!")
        
        return {
            'transients': transients,
            'anomalies': anomalies,
            'report': report
        }

if __name__ == "__main__":
    engine = AstraDiscoveryEngine()
    results = engine.run_discovery_pipeline(days=30)
    
    if results:
        print("\n" + results['report'])
        
        # Save report
        with open('astra_discovery_report.txt', 'w') as f:
            f.write(results['report'])
        print("\n📄 Report saved to: astra_discovery_report.txt")
        
        # Save data
        results['transients'].to_csv('transients_catalog.csv', index=False)
        print("📊 Data saved to: transients_catalog.csv")