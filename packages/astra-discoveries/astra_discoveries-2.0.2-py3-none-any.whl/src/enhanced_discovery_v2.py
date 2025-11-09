#!/usr/bin/env python3
"""
ASTRA: Enhanced Discovery Pipeline v2
Works with available data (no coordinates required for basic scoring)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

try:
    from astroquery.gaia import Gaia
    from astroquery.simbad import Simbad
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    ASTROPY_AVAILABLE = True
except:
    ASTROPY_AVAILABLE = False
    print("⚠️  Astroquery not available, using basic mode")

class EnhancedDiscoveryEngineV2:
    """Enhanced discovery that works with available data"""
    
    def __init__(self):
        self.transients = pd.DataFrame()
        self.anomalies = []
        
    def scrape_rochester_enhanced(self):
        """Enhanced scraping with better pattern matching"""
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
        
        # Pattern for individual transient entries (more flexible)
        pattern = r'(AT\d{4}[\w]+).*?discovered\s+(\d{4}/\d{2}/\d{2})'
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
                
                # Extract RA/Dec if present
                ra_match = re.search(r'R\.A\.\s*=\s*([\dhms\.]+)', context)
                dec_match = re.search(r'Decl\.\s*=\s*([\+\-\d\s\.\']+)', context)
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
            if 'ra' in df.columns:
                has_coords = df['ra'].notna().sum()
                print(f"   📍 Coordinates available for: {has_coords} objects")
        
        return df
    
    def calculate_advanced_score(self, row):
        """Calculate advanced anomaly score"""
        score = 0.0
        reasons = []
        
        # Brightness scoring (more granular)
        if pd.notna(row['mag']):
            if row['mag'] < 14.0:
                score += 5.0
                reasons.append(f"Exceptionally bright (m={row['mag']:.1f})")
            elif row['mag'] < 15.0:
                score += 4.0
                reasons.append(f"Extremely bright (m={row['mag']:.1f})")
            elif row['mag'] < 16.0:
                score += 3.0
                reasons.append(f"Very bright (m={row['mag']:.1f})")
            elif row['mag'] < 17.0:
                score += 2.0
                reasons.append(f"Bright (m={row['mag']:.1f})")
            elif row['mag'] > 21.0:
                score += 2.0
                reasons.append(f"Extremely faint (m={row['mag']:.1f})")
        
        # Type scoring
        type_scores = {
            'unknown': 2.0,
            'unk': 2.0,
            'LRN': 5.0,  # Luminous Red Novae are rare
            'CV': 1.0,
            'Ia': 0.5,   # Normal SN Ia
            'II': 0.5,   # Normal SN II
            'IIP': 0.5,
            'IIn': 3.0,  # Interesting SN IIn
            'Ibn': 4.0,  # Rare SN Ibn
        }
        
        for type_keyword, type_score in type_scores.items():
            if type_keyword in row['type']:
                score += type_score
                if type_score >= 3.0:
                    reasons.append(f"Rare type: {row['type']}")
                break
        else:
            # Unknown type
            if row['type'] not in ['unknown', 'unk', '']:
                score += 1.5
                reasons.append(f"Unusual type: {row['type']}")
        
        return score, reasons
    
    def find_advanced_anomalies(self, transients):
        """Find anomalies using advanced scoring"""
        print("🔍 Finding advanced anomalies...")
        
        anomalies = []
        
        for idx, row in transients.iterrows():
            score, reasons = self.calculate_advanced_score(row)
            
            if score >= 5.0:
                anomaly = {
                    'id': row['id'],
                    'mag': row['mag'],
                    'type': row['type'],
                    'score': score,
                    'reasons': reasons,
                    'source': row['source']
                }
                
                # Add coordinates if available
                if 'ra' in row and pd.notna(row['ra']):
                    anomaly['ra'] = row['ra']
                    anomaly['dec'] = row['dec']
                
                anomalies.append(anomaly)
        
        # Sort by score
        anomalies = sorted(anomalies, key=lambda x: x['score'], reverse=True)
        
        print(f"   🎯 Found {len(anomalies)} advanced anomalies")
        return anomalies
    
    def generate_advanced_report(self, anomalies):
        """Generate advanced discovery report"""
        report = []
        report.append("=" * 80)
        report.append("ASTRA ADVANCED DISCOVERY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        if not anomalies:
            report.append("No high-priority anomalies found.")
            return "\n".join(report)
        
        # Summary stats
        report.append(f"📊 Summary: {len(anomalies)} high-priority anomalies")
        report.append("")
        
        # Top anomalies
        report.append("🎯 HIGH-PRIORITY ANOMALIES (Score ≥ 5.0)")
        report.append("-" * 50)
        report.append("")
        
        for i, obj in enumerate(anomalies, 1):
            report.append(f"{i}. {obj['id']} (Score: {obj['score']:.1f}/10.0)")
            report.append(f"   Magnitude: {obj['mag']:.1f}")
            report.append(f"   Type: {obj['type']}")
            
            if 'ra' in obj:
                report.append(f"   Position: {obj['ra']} {obj['dec']}")
            
            report.append(f"   Reasons: {', '.join(obj['reasons'])}")
            report.append("")
        
        # Follow-up recommendations
        report.append("🔭 IMMEDIATE FOLLOW-UP REQUIRED")
        report.append("-" * 50)
        report.append("")
        
        for i, obj in enumerate(anomalies[:5], 1):
            if obj['score'] >= 7.0:
                priority = "🔴 HIGH"
                timeline = "Within 24 hours"
            elif obj['score'] >= 5.0:
                priority = "🟡 MEDIUM"
                timeline = "Within 3 days"
            else:
                priority = "🟢 LOW"
                timeline = "Within 2 weeks"
            
            report.append(f"{i}. {obj['id']} ({priority}):")
            report.append(f"   Timeline: {timeline}")
            report.append(f"   Action: Spectroscopic classification")
            
            if obj['mag'] < 17:
                report.append(f"   Telescope: 2-4m class (e.g., NOT, INT, LCO)")
            else:
                report.append(f"   Telescope: 8m class (e.g., VLT, Keck)")
            report.append("")
        
        # Science goals
        report.append("🎯 SCIENCE OPPORTUNITIES")
        report.append("-" * 50)
        report.append("")
        
        # Count by type
        types = {}
        for obj in anomalies:
            t = obj['type']
            types[t] = types.get(t, 0) + 1
        
        for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"• {t}: {count} objects")
        
        report.append("")
        report.append("Key opportunities:")
        report.append("• Unknown types: Need spectroscopic classification")
        report.append("• Bright objects: Accessible to small telescopes")
        report.append("• LRN candidates: Rare stellar merger events")
        report.append("• Unusual types: Potential new phenomena")
        
        return "\n".join(report)
    
    def run_advanced_pipeline(self):
        """Run the complete advanced discovery pipeline"""
        print("🚀 ASTRA Advanced Discovery Pipeline Starting...")
        print("=" * 60)
        
        # Phase 1: Scrape data
        transients = self.scrape_rochester_enhanced()
        
        if transients.empty:
            print("❌ No transients found. Aborting.")
            return None
        
        # Phase 2: Find advanced anomalies
        anomalies = self.find_advanced_anomalies(transients)
        
        # Phase 3: Generate advanced report
        report = self.generate_advanced_report(anomalies)
        
        print("=" * 60)
        print("✅ Advanced discovery pipeline complete!")
        
        return {
            'transients': transients,
            'anomalies': anomalies,
            'report': report
        }

if __name__ == "__main__":
    engine = EnhancedDiscoveryEngineV2()
    results = engine.run_advanced_pipeline()
    
    if results:
        print("\n" + results['report'])
        
        # Save advanced report
        with open('astra_advanced_report.txt', 'w') as f:
            f.write(results['report'])
        print("\n📄 Advanced report saved to: astra_advanced_report.txt")
        
        # Save data
        results['transients'].to_csv('advanced_transients_catalog.csv', index=False)
        print("📊 Data saved to: advanced_transients_catalog.csv")
        
        # Show summary
        print(f"\n📈 Discovered {len(results['anomalies'])} high-priority anomalies")
        if results['anomalies']:
            top = results['anomalies'][0]
            print(f"🎯 Top anomaly: {top['id']} (Score: {top['score']:.1f})")
            print(f"   Magnitude: {top['mag']:.1f}, Type: {top['type']}")