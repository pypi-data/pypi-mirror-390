"""
Classification Engine for ASTRA
Attempts to classify unknown transients using multiple methods
"""

import pandas as pd
import numpy as np
import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class ClassificationEngine:
    """
    Multi-method classification engine for astronomical transients.
    
    Methods:
    1. Photometric classification (colors, light curve shape)
    2. Host galaxy analysis (for extragalactic vs. Galactic)
    3. Cross-match with variable star catalogs
    4. Temporal evolution analysis
    5. Spectral energy distribution (SED) fitting
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASTRA-Classification-Engine/2.0'
        })
        
        # Classification confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,      # Very confident
            'medium': 0.6,    # Reasonably confident  
            'low': 0.4        # Tentative
        }
        
        # Known classification schemes
        self.type_hierarchy = {
            'supernova': ['ia', 'ib', 'ic', 'ii', 'iip', 'iin', 'ibn', 'slsn'],
            'variable_star': ['cv', 'nov', 'lbnv', 'mira', 'rrlyr', 'cepheid'],
            'stellar_transient': ['lrn', 'kilonova', 'merger'],
            'active_galaxy': ['agn', 'quasar', 'blazar']
        }
    
    def classify_transient(self, transient_id: str, transient_data: Dict) -> Dict:
        """
        Comprehensive classification of a single transient.
        
        Parameters
        ----------
        transient_id : str
            Object ID (e.g., "AT2025abao")
        transient_data : Dict
            Known data about the transient
            
        Returns
        -------
        Dict
            Classification results with confidence
        """
        logger.info(f"Classifying transient: {transient_id}")
        
        results = {
            'transient_id': transient_id,
            'classification_timestamp': datetime.now().isoformat(),
            'initial_type': transient_data.get('type', 'unk'),
            'initial_score': transient_data.get('anomaly_score', 0),
            'methods_applied': [],
            'classification': 'unknown',
            'confidence': 0.0,
            'evidence': [],
            'recommendations': []
        }
        
        # Method 1: Photometric classification (if multi-band data available)
        photo_class = self._photometric_classification(transient_data)
        if photo_class['confidence'] > 0:
            results['methods_applied'].append('photometric')
            results['evidence'].extend(photo_class['evidence'])
        
        # Method 2: Host galaxy analysis (if coordinates available)
        if 'ra' in transient_data and 'dec' in transient_data:
            host_analysis = self._analyze_host_galaxy(
                transient_data['ra'], transient_data['dec']
            )
            if host_analysis['confidence'] > 0:
                results['methods_applied'].append('host_galaxy')
                results['evidence'].extend(host_analysis['evidence'])
        
        # Method 3: Cross-match with variable star catalogs
        varstar_match = self._match_variable_star_catalogs(transient_data)
        if varstar_match['confidence'] > 0:
            results['methods_applied'].append('variable_star')
            results['evidence'].extend(varstar_match['evidence'])
        
        # Method 4: Temporal evolution analysis (if time series available)
        temporal = self._analyze_temporal_evolution(transient_data)
        if temporal['confidence'] > 0:
            results['methods_applied'].append('temporal')
            results['evidence'].extend(temporal['evidence'])
        
        # Method 5: SED fitting (if multi-band photometry available)
        sed_fit = self._fit_sed(transient_data)
        if sed_fit['confidence'] > 0:
            results['methods_applied'].append('sed_fitting')
            results['evidence'].extend(sed_fit['evidence'])
        
        # Compile final classification
        final_class = self._compile_classification(results['evidence'])
        results['classification'] = final_class['type']
        results['confidence'] = final_class['confidence']
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _photometric_classification(self, transient_data: Dict) -> Dict:
        """
        Classify based on photometric properties.
        
        Uses: colors, magnitude, rate of change
        """
        result = {'type': 'unknown', 'confidence': 0.0, 'evidence': []}
        
        try:
            mag = float(transient_data.get('mag', 99.0))
            
            # Basic photometric classification rules
            if mag < 12:
                result['evidence'].append(f"Very bright (m={mag:.1f}) - likely Galactic")
                
                if mag < 10:
                    result['type'] = 'nova_or_cv'
                    result['confidence'] = 0.6
                    result['evidence'].append("Extremely bright suggests nova or bright CV")
            
            elif mag < 16:
                result['evidence'].append(f"Bright (m={mag:.1f}) - could be SN or LRN")
                
                # Check if type hints exist
                obj_type = transient_data.get('type', '').lower()
                if 'lrn' in obj_type:
                    result['type'] = 'luminous_red_nova'
                    result['confidence'] = 0.7
                    result['evidence'].append("LRN classification from source")
                elif any(sn_type in obj_type for sn_type in ['ia', 'ib', 'ic', 'ii']):
                    result['type'] = 'supernova'
                    result['confidence'] = 0.6
                    result['evidence'].append(f"SN type hint: {obj_type}")
            
            elif mag < 20:
                result['evidence'].append(f"Moderate brightness (m={mag:.1f}) - typical SN")
                result['type'] = 'supernova'
                result['confidence'] = 0.5
            
            else:
                result['evidence'].append(f"Faint (m={mag:.1f}) - distant SN or variable")
                result['confidence'] = 0.3
        
        except Exception as e:
            logger.error(f"Error in photometric classification: {e}")
        
        return result
    
    def _analyze_host_galaxy(self, ra: float, dec: float) -> Dict:
        """
        Analyze host galaxy to determine if extragalactic.
        
        Parameters
        ----------
        ra : float
            Right ascension (degrees)
        dec : float
            Declination (degrees)
            
        Returns
        -------
        Dict
            Host galaxy analysis
        """
        result = {'type': 'unknown', 'confidence': 0.0, 'evidence': []}
        
        try:
            # Query NED for objects at this position
            ned_url = "https://ned.ipac.caltech.edu/cgi-bin/objsearch"
            params = {
                'search_type': 'Near Position Search',
                'lon': ra,
                'lat': dec,
                'radius': 30,  # arcseconds
                'in_csys': 'Equatorial',
                'in_equinox': 'J2000',
                'obj_sort': 'Distance from search position',
                'of': 'json'
            }
            
            response = requests.get(ned_url, params=params, timeout=60)
            
            if response.status_code == 200:
                ned_data = response.json()
                
                if 'Preferred' in ned_data and ned_data['Preferred']:
                    nearest = ned_data['Preferred'][0]
                    obj_type = nearest.get('Type', 'Unknown')
                    distance = nearest.get('Distance', 999)
                    
                    result['evidence'].append(f"NED object within 30 arcsec: {obj_type}")
                    
                    if 'Galaxy' in obj_type or 'G' in obj_type:
                        result['type'] = 'extragalactic'
                        result['confidence'] = 0.7
                        result['evidence'].append(f"Host galaxy detected (type: {obj_type})")
                        result['evidence'].append("Strong evidence for extragalactic transient (SN, LRN, etc.)")
                    
                    elif 'Star' in obj_type:
                        result['type'] = 'galactic'
                        result['confidence'] = 0.6
                        result['evidence'].append("Stellar object - likely Galactic variable")
                    
                    else:
                        result['evidence'].append(f"Unclassified NED object: {obj_type}")
                else:
                    result['evidence'].append("No NED objects within 30 arcsec")
                    result['confidence'] = 0.4
                    result['type'] = 'likely_extragalactic'
                    result['evidence'].append("No host detected - could be distant SN")
        
        except Exception as e:
            logger.error(f"Error in host galaxy analysis: {e}")
            result['evidence'].append("Host galaxy analysis failed (network error)")
        
        return result
    
    def _match_variable_star_catalogs(self, transient_data: Dict) -> Dict:
        """
        Cross-match with known variable stars.
        
        Catalogs: VSX (AAVSO), GCVS, etc.
        """
        result = {'type': 'unknown', 'confidence': 0.0, 'evidence': []}
        
        try:
            # Use VSX (AAVSO) catalog via VizieR
            vizier_url = "http://vizier.u-strasbg.fr/viz-bin/votable"
            
            # This is a simplified query - would need proper coordinates
            if 'ra' in transient_data and 'dec' in transient_data:
                params = {
                    '-source': 'B/vsx/vsx',
                    '-c': f"{transient_data['ra']},{transient_data['dec']}",
                    '-c.rs': 30,  # arcseconds
                    '-out.max': 1
                }
                
                response = requests.get(vizier_url, params=params, timeout=30)
                
                if response.status_code == 200 and 'TABLE' in response.text:
                    result['type'] = 'known_variable'
                    result['confidence'] = 0.8
                    result['evidence'].append("Match in VSX variable star catalog")
                    result['evidence'].append("This is a known variable star, not a new transient")
                else:
                    result['evidence'].append("No match in variable star catalogs")
                    result['confidence'] = 0.3
        
        except Exception as e:
            logger.error(f"Error in variable star matching: {e}")
        
        return result
    
    def _analyze_temporal_evolution(self, transient_data: Dict) -> Dict:
        """
        Analyze light curve for classification clues.
        
        Looks for: rise time, decline rate, variability patterns
        """
        result = {'type': 'unknown', 'confidence': 0.0, 'evidence': []}
        
        try:
            # Check if we have historical data
            if 'discovery_date' in transient_data:
                disc_date = pd.to_datetime(transient_data['discovery_date'])
                days_since = (pd.Timestamp.now() - disc_date).days
                
                result['evidence'].append(f"Discovered {days_since} days ago")
                
                if days_since < 7:
                    result['evidence'].append("Very recent - still in early phase")
                    
                    # Young transients are likely SNe or outbursts
                    if days_since < 3:
                        result['type'] = 'recent_outburst'
                        result['confidence'] = 0.5
                        result['evidence'].append("Extremely recent - could be SN or nova")
        
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
        
        return result
    
    def _fit_sed(self, transient_data: Dict) -> Dict:
        """
        Fit spectral energy distribution for classification.
        
        Requires multi-band photometry
        """
        result = {'type': 'unknown', 'confidence': 0.0, 'evidence': []}
        
        try:
            # Check for multi-band data
            bands = []
            for key in transient_data.keys():
                if 'mag_' in key or '_' in key and key.split('_')[-1] in ['u', 'g', 'r', 'i', 'z']:
                    bands.append(key)
            
            if len(bands) >= 2:
                result['evidence'].append(f"Multi-band photometry available: {', '.join(bands)}")
                result['confidence'] = 0.4
                
                # Simple color-based classification
                if 'mag_g' in transient_data and 'mag_r' in transient_data:
                    g_r = float(transient_data['mag_g']) - float(transient_data['mag_r'])
                    
                    if g_r > 1.0:
                        result['evidence'].append(f"Red color (g-r = {g_r:.1f}) - could be LRN or SN II")
                    elif g_r < 0.5:
                        result['evidence'].append(f"Blue color (g-r = {g_r:.1f}) - could be SN Ia or CV")
        
        except Exception as e:
            logger.error(f"Error in SED fitting: {e}")
        
        return result
    
    def _compile_classification(self, evidence: List[str]) -> Dict:
        """
        Compile evidence into final classification.
        
        Parameters
        ----------
        evidence : List[str]
            List of evidence statements
            
        Returns
        -------
        Dict
            {'type': classification, 'confidence': score}
        """
        if not evidence:
            return {'type': 'unknown', 'confidence': 0.0}
        
        # Count evidence for each type
        type_votes = {}
        confidence_scores = []
        
        for statement in evidence:
            # Extract confidence from statement
            if 'confidence' in statement.lower():
                try:
                    # Look for numbers in statement
                    import re
                    nums = re.findall(r'([0-9.]+)', statement)
                    if nums:
                        confidence_scores.append(float(nums[0]))
                except:
                    pass
            
            # Count type mentions
            statement_lower = statement.lower()
            
            if any(word in statement_lower for word in ['lrn', 'red nova', 'merger']):
                type_votes['luminous_red_nova'] = type_votes.get('luminous_red_nova', 0) + 1
            
            if any(word in statement_lower for word in ['supernova', 'sn ', 'ia', 'ib', 'ic', 'ii']):
                type_votes['supernova'] = type_votes.get('supernova', 0) + 1
            
            if any(word in statement_lower for word in ['variable', 'cv', 'nova', 'outburst']):
                type_votes['variable_star'] = type_votes.get('variable_star', 0) + 1
            
            if any(word in statement_lower for word in ['extragalactic', 'galaxy', 'host']):
                type_votes['extragalactic'] = type_votes.get('extragalactic', 0) + 1
            
            if any(word in statement_lower for word in ['galactic', 'stellar']):
                type_votes['galactic'] = type_votes.get('galactic', 0) + 1
        
        # Determine most likely type
        if type_votes:
            best_type = max(type_votes, key=type_votes.get)
            vote_count = type_votes[best_type]
            total_votes = sum(type_votes.values())
            
            # Confidence based on vote proportion
            vote_confidence = vote_count / total_votes
            
            # Combine with explicit confidence scores
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                final_confidence = 0.6 * vote_confidence + 0.4 * avg_confidence
            else:
                final_confidence = vote_confidence * 0.7  # Scale down if no explicit scores
            
            return {
                'type': best_type,
                'confidence': min(final_confidence, 1.0)
            }
        
        # Default if no clear type emerges
        return {'type': 'unknown', 'confidence': 0.2}
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate follow-up recommendations based on classification."""
        recommendations = []
        
        classification = results['classification']
        confidence = results['confidence']
        
        if confidence < 0.5:
            recommendations.append("🔬 Spectroscopic classification urgently needed")
            recommendations.append("Target for 2-4m telescope (e.g., NOT, LCO, SAAO)")
        
        elif classification == 'luminous_red_nova':
            recommendations.append("🌟 Potential LRN - extremely rare and valuable")
            recommendations.append("High priority for spectroscopy and photometry")
            recommendations.append("Monitor for dust formation and IR excess")
        
        elif classification == 'supernova':
            recommendations.append("💥 Supernova classification needed")
            recommendations.append("Obtain spectrum to determine type (Ia/Ib/Ic/II)")
            recommendations.append("Photometric monitoring for light curve")
        
        elif classification == 'variable_star':
            recommendations.append("🔄 Likely Galactic variable star")
            recommendations.append("Check if known in VSX catalog")
            recommendations.append("Photometric monitoring to determine period")
        
        # Always add these
        recommendations.append("📊 Submit classification to TNS if new type")
        recommendations.append("📄 Consider publication if rare/interesting")
        
        return recommendations
    
    def classify_all_transients(self, transients_df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify all transients in a DataFrame.
        
        Parameters
        ----------
        transients_df : pd.DataFrame
            Transients to classify
            
        Returns
        -------
        pd.DataFrame
            Transients with classification results
        """
        if transients_df.empty:
            return transients_df
        
        logger.info(f"Classifying {len(transients_df)} transients")
        
        classifications = []
        
        for _, transient in transients_df.iterrows():
            result = self.classify_transient(
                transient.get('id', 'unknown'),
                transient.to_dict()
            )
            classifications.append(result)
        
        # Add classification results to DataFrame
        transients_df['classification'] = [c['classification'] for c in classifications]
        transients_df['classification_confidence'] = [c['confidence'] for c in classifications]
        transients_df['classification_evidence'] = [c['evidence'] for c in classifications]
        transients_df['classification_recommendations'] = [c['recommendations'] for c in classifications]
        
        return transients_df


def generate_classification_report(transient_id: str, classification_results: Dict, output_file: Optional[str] = None) -> str:
    """
    Generate a formatted classification report.
    
    Parameters
    ----------
    transient_id : str
        Object ID
    classification_results : Dict
        Results from ClassificationEngine
    output_file : str, optional
        Path to save report
        
    Returns
    -------
    str
        Formatted report
    """
    report = f"""═══════════════════════════════════════════════════════════
ASTRA CLASSIFICATION REPORT
═══════════════════════════════════════════════════════════

Object: {transient_id}
Classification Time: {classification_results['classification_timestamp']}

INITIAL PARAMETERS
──────────────────
Type (from source): {classification_results['initial_type']}
Anomaly Score: {classification_results['initial_score']}/10

CLASSIFICATION RESULTS
─────────────────────
Best Classification: {classification_results['classification'].upper()}
Confidence: {classification_results['confidence']:.1f}/1.0

METHODS APPLIED
───────────────
"""
    
    for method in classification_results['methods_applied']:
        report += f"• {method.replace('_', ' ').title()}\n"
    
    report += f"""
EVIDENCE SUMMARY
────────────────
"""
    
    for i, evidence in enumerate(classification_results['evidence'], 1):
        report += f"{i}. {evidence}\n"
    
    report += f"""
RECOMMENDATIONS
───────────────
"""
    
    for i, rec in enumerate(classification_results['recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    # Add confidence interpretation
    conf = classification_results['confidence']
    if conf >= 0.8:
        conf_level = "HIGH"
    elif conf >= 0.6:
        conf_level = "MEDIUM"
    elif conf >= 0.4:
        conf_level = "LOW"
    else:
        conf_level = "VERY LOW"
    
    report += f"""
CONFIDENCE ASSESSMENT
─────────────────────
Level: {conf_level} ({conf:.1f}/1.0)

{"✅ Classification reliable" if conf >= 0.6 else "⚠️ Classification uncertain - spectroscopy needed"}

═══════════════════════════════════════════════════════════
"""
    
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)
    
    return report


if __name__ == "__main__":
    # Test classification on our discoveries
    print("🔬 ASTRA Classification Engine Test")
    print("=" * 60)
    
    engine = ClassificationEngine()
    
    # Test data for our top discoveries
    test_transients = [
        {
            'id': 'AT2025abao',
            'mag': 15.1,
            'type': 'LRN',
            'anomaly_score': 8.0,
            'discovery_date': '2025-11-06'
        },
        {
            'id': 'AT2025acfl',
            'mag': 16.2,
            'type': 'unk',
            'anomaly_score': 5.5,
            'discovery_date': '2025-11-06'
        },
        {
            'id': 'AT2025zov',
            'mag': 15.5,
            'type': 'unk',
            'anomaly_score': 5.0,
            'discovery_date': '2025-11-05'
        }
    ]
    
    for transient in test_transients:
        print(f"\nClassifying {transient['id']}...")
        results = engine.classify_transient(transient['id'], transient)
        
        print(f"  Classification: {results['classification']}")
        print(f"  Confidence: {results['confidence']:.1f}/1.0")
        print(f"  Methods: {', '.join(results['methods_applied'])}")
        
        # Print top recommendation
        if results['recommendations']:
            print(f"  → {results['recommendations'][0]}")
    
    print("\n" + "=" * 60)
    print("✅ Classification complete!")