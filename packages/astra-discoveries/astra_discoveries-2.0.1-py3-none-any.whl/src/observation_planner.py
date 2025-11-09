#!/usr/bin/env python3
"""
ASTRA: Observation Planner for High-Priority Transients
Generates detailed observation plans for follow-up studies
"""

import math
from datetime import datetime, timedelta

class ObservationPlanner:
    """Generate detailed observation plans for transients"""
    
    def __init__(self):
        self.observatories = {
            "VLT": {"location": "Chile", "aperture": 8.2, "instruments": ["XSHOOTER", "FORS2", "MUSE"]},
            "Keck": {"location": "Hawaii", "aperture": 10.0, "instruments": ["LRIS", "DEIMOS", "ESI"]},
            "LBT": {"location": "Arizona", "aperture": 8.4, "instruments": ["MODS", "LUCI"]},
            "Gemini-N": {"location": "Hawaii", "aperture": 8.1, "instruments": ["GMOS", "NIRI"]},
            "Gemini-S": {"location": "Chile", "aperture": 8.1, "instruments": ["GMOS", "FLAMINGOS"]},
        }
        
    def calculate_airmass(self, declination: float, latitude: float = 19.8, lst: float = None) -> Dict:
        """Calculate approximate airmass for a target"""
        # Simplified airmass calculation
        if lst is None:
            # Use transit time (optimal)
            hour_angle = 0
        else:
            # Approximate hour angle
            hour_angle = lst - 0  # Assuming RA ~ LST at transit
            
        # Zenith distance approximation
        declination_rad = math.radians(declination)
        latitude_rad = math.radians(latitude)
        
        # Simplified: best airmass at transit
        zenith_distance = abs(declination - latitude)
        zenith_distance_rad = math.radians(zenith_distance)
        
        # Airmass approximation
        airmass = 1 / math.cos(zenith_distance_rad)
        
        return {
            "airmass": min(airmass, 3.0),  # Cap at 3
            "zenith_distance_deg": zenith_distance,
            "optimal": airmass < 1.5
        }
    
    def parse_coordinates(self, ra_str: str, dec_str: str) -> Tuple[float, float]:
        """Parse RA/Dec strings to degrees"""
        # Parse RA
        ra_parts = ra_str.replace("h", " ").replace("m", " ").replace("s", "").split()
        ra_hours = float(ra_parts[0]) + float(ra_parts[1])/60 + float(ra_parts[2])/3600
        ra_deg = ra_hours * 15  # Convert hours to degrees
        
        # Parse Dec
        dec_parts = dec_str.replace("d", " ").replace("m", " ").replace("s", "").split()
        dec_deg = float(dec_parts[0]) + float(dec_parts[1])/60 + float(dec_parts[2])/3600
        if dec_str.startswith("-"):
            dec_deg = -dec_deg
            
        return ra_deg, dec_deg
    
    def generate_observation_plan(self, target: Dict) -> str:
        """Generate detailed observation plan for a target"""
        
        ra_deg, dec_deg = self.parse_coordinates(target["ra"], target["dec"])
        
        plan = []
        plan.append("=" * 80)
        plan.append(f"OBSERVATION PLAN: {target['id']} ({target['name']})")
        plan.append("=" * 80)
        plan.append("")
        
        # Basic info
        plan.append(f"Target: {target['id']}")
        plan.append(f"Coordinates: RA={ra_deg:.4f}°, Dec={dec_deg:.4f}°")
        plan.append(f"Current Magnitude: {target['mag']:.1f}")
        plan.append(f"Classification: {target['type']}")
        plan.append(f"Discovery Date: {target['date']}")
        plan.append("")
        
        # Observability
        airmass_info = self.calculate_airmass(dec_deg)
        plan.append("--- OBSERVABILITY ---")
        plan.append(f"Declination: {dec_deg:.1f}°")
        
        if abs(dec_deg) < 30:
            plan.append("Visibility: Good from both hemispheres")
        elif dec_deg > 30:
            plan.append("Visibility: Best from Northern hemisphere")
        else:
            plan.append("Visibility: Best from Southern hemisphere")
            
        plan.append(f"Optimal airmass: {airmass_info['airmass']:.2f}")
        plan.append(f"Airmass status: {'EXCELLENT' if airmass_info['optimal'] else 'ACCEPTABLE'}")
        plan.append("")
        
        # Recommended observations
        plan.append("--- RECOMMENDED OBSERVATIONS ---")
        
        if "CV" in target["type"]:
            plan.append("SPECTROSCOPY (HIGHEST PRIORITY):")
            plan.append("  • Instrument: Low-resolution spectrograph")
            plan.append("  • Wavelength: 4000-7000 Å (cover Hα, Hβ, He lines)")
            plan.append("  • Exposure: 300-600s for S/N>20 at current mag")
            plan.append("  • Goal: Identify emission lines, measure accretion state")
            plan.append("")
            plan.append("PHOTOMETRY:")
            plan.append("  • Bands: g, r, i (or B, V, R)")
            plan.append("  • Cadence: Every 2 hours for first night")
            plan.append("  • Goal: Determine outburst type (dwarf nova vs. nova-like)")
            plan.append("")
            
        elif "SN" in target["type"] or "unknown" in target["type"]:
            plan.append("SPECTROSCOPY:")
            plan.append("  • Instrument: Medium-resolution spectrograph")
            plan.append("  • Wavelength: 3500-9000 Å (full optical range)")
            plan.append("  • Exposure: 900-1800s depending on telescope aperture")
            plan.append("  • Goal: Classification, redshift measurement")
            plan.append("")
            plan.append("PHOTOMETRY:")
            plan.append("  • Bands: g, r, i, z (or UBVRI)")
            plan.append("  • Cadence: Daily for 2 weeks")
            plan.append("  • Goal: Light curve classification, peak magnitude")
            plan.append("")
            
        elif "GRB" in target["type"]:
            plan.append("RAPID FOLLOW-UP (URGENT):")
            plan.append("  • Multi-band photometry every 15 minutes for first 2 hours")
            plan.append("  • Spectroscopy ASAP (within 24 hours if possible)")
            plan.append("  • X-ray/UV observations if space-based resources available")
            plan.append("")
        
        # Recommended telescopes
        plan.append("--- RECOMMENDED TELESCOPES ---")
        
        if target["mag"] < 16:
            # Bright target - smaller telescopes OK
            plan.append("Primary: 2-4m class (e.g., NOT, INT, LCO)")
            plan.append("Secondary: 8m class for spectroscopy")
            plan.append("Amateur: CCD photometry possible with 30cm+")
        elif target["mag"] < 18:
            # Medium brightness
            plan.append("Primary: 4-8m class (e.g., VLT, Keck, Gemini)")
            plan.append("Secondary: 10m+ for high-S/N spectroscopy")
        else:
            # Faint target
            plan.append("Primary: 8-10m class (VLT, Keck, LBT)")
            plan.append("Secondary: JWST if IR observations needed")
            
        plan.append("")
        
        # Timeline
        plan.append("--- OBSERVING TIMELINE ---")
        discovery_date = datetime.strptime(target["date"], "%Y-%m-%d")
        
        plan.append(f"Day 0 (Discovery): {discovery_date.strftime('%Y-%m-%d')}")
        plan.append(f"Day +1-3: Photometric monitoring, initial classification")
        plan.append(f"Day +3-7: Spectroscopic confirmation")
        plan.append(f"Day +7-30: Light curve monitoring, evolution study")
        plan.append("")
        
        # Expected outcomes
        plan.append("--- EXPECTED OUTCOMES ---")
        if "CV" in target["type"]:
            plan.append("• Distance: 100-500 pc (if typical CV absolute magnitude)")
            plan.append("• Outburst amplitude: 2-5 magnitudes typical")
            plan.append("• Recurrence: Days to weeks if dwarf nova")
            plan.append("• Spectra: Strong Balmer emission, possibly He II")
        elif "unknown" in target["type"]:
            plan.append("• Could be supernova at z=0.1-0.5")
            plan.append("• Or nearby Galactic variable (if extinction low)")
            plan.append("• Spectra will distinguish extragalactic vs. Galactic")
        elif "GRB" in target["type"]:
            plan.append("• Redshift: z=0.5-3 typical for GRBs")
            plan.append("• Afterglow decay: Power law with index α~1-2")
            plan.append("• Host galaxy: Faint, star-forming")
            
        return "\n".join(plan)
    
    def generate_all_plans(self):
        """Generate observation plans for all targets"""
        
        targets = [
            {"id": "AT2025aaxb", "name": "TCP J22285154+5317431", "mag": 15.6, 
             "date": "2025-10-17", "type": "CV?", "ra": "22h28m51.54s", "dec": "+53d17m43.1s"},
            
            {"id": "AT2025aavs", "name": "TCP J05425058+4148205", "mag": 15.6,
             "date": "2025-10-18", "type": "CV?", "ra": "05h42m50.58s", "dec": "+41d48m20.5s"},
             
            {"id": "AT2025aayo", "name": "AT2025aayo", "mag": 20.4,
             "date": "2025-10-19", "type": "unknown", "ra": "01h40m04.13s", "dec": "+23d25m54.1s"},
        ]
        
        for target in targets:
            print(f"\nGenerating plan for {target['id']}...")
            plan = self.generate_observation_plan(target)
            
            filename = f"/Volumes/VIXinSSD/astra/plan_{target['id']}.txt"
            with open(filename, "w") as f:
                f.write(plan)
            
            print(f"Saved to: {filename}")

if __name__ == "__main__":
    planner = ObservationPlanner()
    planner.generate_all_plans()
    
    print("\n" + "=" * 80)
    print("All observation plans generated successfully!")
    print("=" * 80)