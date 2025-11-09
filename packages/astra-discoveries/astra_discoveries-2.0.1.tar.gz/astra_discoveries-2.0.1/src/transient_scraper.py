#!/usr/bin/env python3
"""
ASTRA: Transient Scraper Module
Data collection from public transient sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta

class TransientScraper:
    """Scraper for public transient data sources"""
    
    def __init__(self):
        self.sources = {
            'rochester': 'http://www.rochesterastronomy.org/supernova.html',
        }
    
    def scrape_rochester_page(self):
        """Scrape the Rochester Astronomy Supernova page."""
        return scrape_rochester_sn_page()
    
    def get_recent_transients(self, days=7):
        """Get recent transients from all sources."""
        return get_recent_transients(days=days)


def scrape_rochester_sn_page():
    """Scrape Rochester Astronomy Supernova page for recent transients."""
    url = "http://www.rochesterastronomy.org/supernova.html"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    
    transients = []
    
    # Look for tables with transient data
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
            
        # Check if this looks like a transient table
        first_row = rows[0].get_text()
        if 'Name' in first_row and 'Mag' in first_row:
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
    
    if not df.empty:
        # Remove duplicates, keeping the one with most info
        df = df.sort_values('source', key=lambda x: x.map({'Rochester_Entries': 1, 'Rochester_Table_1': 0}))
        df = df.drop_duplicates('id', keep='first')
    
    return df


def scrape_tns_public():
    """Scrape TNS public pages (no API key needed for basic info)."""
    # This is a placeholder - TNS requires API key for programmatic access
    return pd.DataFrame()


def get_recent_transients(days=7):
    """Get transients from all available public sources."""
    print("Scraping Rochester Supernova page...")
    rochester_data = scrape_rochester_sn_page()
    
    # Filter for recent transients (last N days)
    if not rochester_data.empty:
        rochester_data['date'] = pd.to_datetime(rochester_data['date'], errors='coerce')
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        recent = rochester_data[rochester_data['date'] > cutoff]
        print(f"Found {len(recent)} transients from last {days} days")
        return recent
    
    return pd.DataFrame()


if __name__ == "__main__":
    df = get_recent_transients(30)
    print(f"\nTotal transients found: {len(df)}")
    if not df.empty:
        print(df.head())