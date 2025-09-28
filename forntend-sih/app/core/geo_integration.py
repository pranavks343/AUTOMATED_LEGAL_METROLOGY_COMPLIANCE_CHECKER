"""
Geographic Data Integration Module
Handles location data collection and geo-tagging for compliance monitoring
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class LocationData:
    """Represents geographic location information"""
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0
    source: str = "unknown"  # 'ip', 'address', 'manual', 'seller_data'

class GeoLocationService:
    """Service for handling geographic location operations"""
    
    def __init__(self):
        self.ip_api_base = "http://ip-api.com/json/"
        self.geocoding_cache = {}
        
    def get_location_from_ip(self, ip_address: str) -> Optional[LocationData]:
        """Get location data from IP address using ip-api.com (free service)"""
        try:
            if ip_address in ['127.0.0.1', 'localhost']:
                # Return sample location for localhost
                return LocationData(
                    latitude=28.7041,
                    longitude=77.1025,
                    city="New Delhi",
                    state="Delhi",
                    country="India",
                    confidence=0.8,
                    source="ip_localhost"
                )
            
            response = requests.get(f"{self.ip_api_base}{ip_address}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    return LocationData(
                        latitude=data.get('lat', 0.0),
                        longitude=data.get('lon', 0.0),
                        city=data.get('city'),
                        state=data.get('regionName'),
                        country=data.get('country'),
                        postal_code=data.get('zip'),
                        confidence=0.7,
                        source="ip_geolocation"
                    )
                    
        except Exception as e:
            logger.error(f"IP geolocation failed for {ip_address}: {e}")
            
        return None
    
    def geocode_address(self, address: str) -> Optional[LocationData]:
        """Geocode an address to get coordinates (using free services)"""
        try:
            # Use Nominatim (OpenStreetMap) for free geocoding
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in'  # Limit to India
            }
            
            headers = {
                'User-Agent': 'LegalMetrologyChecker/1.0'
            }
            
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json()
                
                if results:
                    result = results[0]
                    return LocationData(
                        latitude=float(result['lat']),
                        longitude=float(result['lon']),
                        address=result.get('display_name'),
                        confidence=0.8,
                        source="address_geocoding"
                    )
                    
        except Exception as e:
            logger.error(f"Address geocoding failed for {address}: {e}")
            
        return None
    
    def extract_location_from_text(self, text: str) -> List[LocationData]:
        """Extract potential location information from text using pattern matching"""
        locations = []
        
        # Indian state patterns
        indian_states = [
            'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Rajasthan',
            'Uttar Pradesh', 'West Bengal', 'Madhya Pradesh', 'Haryana', 'Punjab',
            'Delhi', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Odisha',
            'Jharkhand', 'Assam', 'Bihar', 'Chhattisgarh', 'Himachal Pradesh'
        ]
        
        # City patterns (major Indian cities)
        major_cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur',
            'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Patna'
        ]
        
        # State coordinates mapping
        state_coords = {
            'Maharashtra': (19.7515, 75.7139),
            'Karnataka': (15.3173, 75.7139),
            'Tamil Nadu': (11.1271, 78.6569),
            'Gujarat': (23.0225, 72.5714),
            'Rajasthan': (27.0238, 74.2179),
            'Uttar Pradesh': (26.8467, 80.9462),
            'West Bengal': (22.5726, 88.3639),
            'Madhya Pradesh': (22.9734, 78.6569),
            'Haryana': (29.0588, 76.0856),
            'Punjab': (31.1471, 75.3412),
            'Delhi': (28.7041, 77.1025),
            'Telangana': (17.1232, 79.2088),
            'Andhra Pradesh': (15.9129, 79.7400),
            'Kerala': (10.8505, 76.2711),
            'Odisha': (20.9517, 85.0985)
        }
        
        text_upper = text.upper()
        
        # Look for states
        for state in indian_states:
            if state.upper() in text_upper:
                if state in state_coords:
                    lat, lon = state_coords[state]
                    locations.append(LocationData(
                        latitude=lat,
                        longitude=lon,
                        state=state,
                        country="India",
                        confidence=0.6,
                        source="text_extraction"
                    ))
        
        return locations

class GeoTaggingManager:
    """Manages geo-tagging of compliance data"""
    
    def __init__(self):
        self.geo_service = GeoLocationService()
        self.location_cache = {}
        
    def tag_validation_record(self, validation_data: Dict[str, Any], 
                            ip_address: Optional[str] = None,
                            seller_address: Optional[str] = None) -> Dict[str, Any]:
        """Add geographic tags to a validation record"""
        
        location_data = []
        
        # Try IP geolocation
        if ip_address:
            ip_location = self.geo_service.get_location_from_ip(ip_address)
            if ip_location:
                location_data.append(ip_location)
        
        # Try seller address geocoding
        if seller_address:
            address_location = self.geo_service.geocode_address(seller_address)
            if address_location:
                location_data.append(address_location)
        
        # Extract location from product text
        product_text = ""
        if 'fields' in validation_data:
            fields = validation_data['fields']
            product_text = f"{fields.get('manufacturer_name', '')} {fields.get('country_of_origin', '')}"
        
        if product_text.strip():
            text_locations = self.geo_service.extract_location_from_text(product_text)
            location_data.extend(text_locations)
        
        # Choose best location (highest confidence)
        best_location = None
        if location_data:
            best_location = max(location_data, key=lambda x: x.confidence)
        
        # Add geographic metadata
        validation_data['geographic_data'] = {
            'primary_location': {
                'latitude': best_location.latitude if best_location else None,
                'longitude': best_location.longitude if best_location else None,
                'city': best_location.city if best_location else None,
                'state': best_location.state if best_location else None,
                'country': best_location.country if best_location else None,
                'confidence': best_location.confidence if best_location else 0.0,
                'source': best_location.source if best_location else None,
                'tagged_at': datetime.now().isoformat()
            },
            'all_locations': [
                {
                    'latitude': loc.latitude,
                    'longitude': loc.longitude,
                    'city': loc.city,
                    'state': loc.state,
                    'country': loc.country,
                    'confidence': loc.confidence,
                    'source': loc.source
                } for loc in location_data
            ]
        }
        
        return validation_data
    
    def get_compliance_by_location(self, validation_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Aggregate compliance data by geographic location"""
        
        location_stats = {}
        
        for record in validation_records:
            geo_data = record.get('geographic_data', {})
            primary_loc = geo_data.get('primary_location', {})
            
            state = primary_loc.get('state')
            if not state:
                continue
                
            if state not in location_stats:
                location_stats[state] = {
                    'state': state,
                    'total_products': 0,
                    'compliant_products': 0,
                    'total_score': 0.0,
                    'violation_count': 0,
                    'latitude': primary_loc.get('latitude'),
                    'longitude': primary_loc.get('longitude')
                }
            
            stats = location_stats[state]
            stats['total_products'] += 1
            stats['total_score'] += record.get('score', 0)
            
            if record.get('is_compliant', False):
                stats['compliant_products'] += 1
            else:
                stats['violation_count'] += len(record.get('issues', []))
        
        # Convert to DataFrame
        location_data = []
        for state, stats in location_stats.items():
            if stats['total_products'] > 0:
                location_data.append({
                    'State': stats['state'],
                    'Compliance_Rate': (stats['compliant_products'] / stats['total_products']) * 100,
                    'Average_Score': stats['total_score'] / stats['total_products'],
                    'Total_Products': stats['total_products'],
                    'Violations': stats['violation_count'],
                    'Latitude': stats['latitude'],
                    'Longitude': stats['longitude']
                })
        
        return pd.DataFrame(location_data)

def get_user_location_from_streamlit() -> Optional[LocationData]:
    """Get user location from Streamlit session (if available)"""
    try:
        import streamlit as st
        
        # Check if location is already in session state
        if 'user_location' in st.session_state:
            return st.session_state.user_location
        
        # Try to get from browser (this would require JavaScript integration)
        # For now, return a default location
        default_location = LocationData(
            latitude=28.7041,
            longitude=77.1025,
            city="New Delhi",
            state="Delhi",
            country="India",
            confidence=0.5,
            source="default"
        )
        
        st.session_state.user_location = default_location
        return default_location
        
    except Exception as e:
        logger.error(f"Failed to get user location: {e}")
        return None

# Global instance
geo_tagging_manager = GeoTaggingManager()

def get_geo_tagging_manager() -> GeoTaggingManager:
    """Get the global geo-tagging manager instance"""
    return geo_tagging_manager
