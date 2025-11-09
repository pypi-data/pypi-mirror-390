#!/usr/bin/env python3
"""
ASTRA: Bright Transient Survey Scraper
Fetches bright transients from public sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_bright_transient_survey():
    """Scrape Bright Transient Survey data from public sources"""
    print("🌐 Scraping Bright Transient Survey sources...")
    
    transients = []
    
    # Try ATLAS forced photometry
    try:
        print("   Checking ATLAS...")
        # ATLAS has a public page but it's not easily scrapeable
        # This is a placeholder for future implementation
    except:
        pass
    
    # Try ZTF public data
    try:
        print("   Checking ZTF public releases...")
        url = "https://www.ztf.caltech.edu/ztf-public-releases.html"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for recent data releases
            links = soup.find_all('a', string=re.compile(r'DR|Data Release', re.I))
            print(f"   Found {len(links)} data release links")
    except Exception as e:
        print(f"   ✗ ZTF error: {e}")
    
    # Try AAVSO
    try:
        print("   Checking AAVSO recent observations...")
        url = "https://www.aavso.org/apps/vsp/"
        # AAVSO has API but requires key
    except:
        pass
    
    return pd.DataFrame(transients)

def scrape_tns_public_pages():
    """Scrape TNS public pages (no API key)"""
    print("🌐 Scraping TNS public pages...")
    
    transients = []
    
    try:
        # TNS recent objects page
        url = "https://www.wis-tns.org/"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for recent transients listed
            # This is limited without API access
    except Exception as e:
        print(f"   ✗ TNS error: {e}")
    
    return pd.DataFrame(transients)

def get_all_bright_transients():
    """Collect bright transients from all sources"""
    print("🚀 Collecting bright transients from all sources...")
    
    all_data = []
    
    # From Rochester page (bright ones)
    print("   From Rochester page...")
    url = "http://www.rochesterastronomy.org/supernova.html"
    resp = requests.get(url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Find the main table (usually first few tables)
    tables = soup.find_all('table')
    for table in tables[:5]:  # Check first 5 tables
        rows = table.find_all('tr')
        if len(rows) < 10:  # Skip small tables
            continue
            
        for row in rows[1:]:  # Skip header
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                try:
                    name = cols[0].get_text(strip=True)
                    mag_str = cols[1].get_text(strip=True)
                    obj_type = cols[2].get_text(strip=True)
                    
                    # Extract magnitude
                    mag = None
                    if mag_str and mag_str != '-':
                        mag_match = re.search(r'([\d\.]+)', mag_str)
                        if mag_match:
                            mag = float(mag_match.group(1))
                    
                    # Only keep bright ones (mag < 17)
                    if name and mag and mag < 17.0:
                        all_data.append({
                            'id': name,
                            'mag': mag,
                            'type': obj_type,
                            'source': 'Rochester_Bright'
                        })
                except:
                    continue
    
    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.drop_duplicates('id')
        print(f"   ✓ Found {len(df)} bright transients (m < 17)")
    
    return df

if __name__ == "__main__":
    bright_transients = get_all_bright_transients()
    print(f"\n📊 Total bright transients: {len(bright_transients)}")
    
    if not bright_transients.empty:
        print("\nTop 10 brightest:")
        print(bright_transients.sort_values('mag').head(10).to_string())
        
        # Save to file
        bright_transients.to_csv('bright_transients.csv', index=False)
        print("\n💾 Saved to bright_transients.csv")