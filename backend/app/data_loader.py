import pandas as pd
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Simple path resolution
def get_data_dir():
    """Get data directory path"""
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "data",  # From backend/app/
        Path("/opt/render/project/src/data"),          # Render absolute path
        Path("data"),                                   # Relative from run location
        Path("../../data"),                            # Two levels up
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found data directory at: {path}")
            return path
    
    # Default to first option
    logger.warning(f"Data directory not found, using default: {possible_paths[0]}")
    return possible_paths[0]

DATA_DIR = get_data_dir()

# Cache for loaded data
_data_cache = None

def load_csv_data(force_reload=False):
    """Load all CSV files into pandas DataFrames with caching"""
    global _data_cache
    
    if _data_cache is not None and not force_reload:
        return _data_cache
    
    try:
        logger.info(f"Loading CSV files from {DATA_DIR}")
        
        # Check if files exist
        required_files = [
            "service_master.csv",
            "bsk_master.csv",
            "deo_master.csv",
            "provision.csv"
        ]
        
        for filename in required_files:
            filepath = DATA_DIR / filename
            if not filepath.exists():
                logger.error(f"❌ Required file not found: {filepath}")
                return None
        
        # Load with proper encoding
        services_df = pd.read_csv(DATA_DIR / "service_master.csv", encoding='utf-8')
        bsks_df = pd.read_csv(DATA_DIR / "bsk_master.csv", encoding='utf-8')
        deos_df = pd.read_csv(DATA_DIR / "deo_master.csv", encoding='utf-8')
        provisions_df = pd.read_csv(DATA_DIR / "provision.csv", encoding='cp1252')
        
        # Clean data - fill NaN values
        services_df = services_df.fillna('')
        bsks_df = bsks_df.fillna('')
        deos_df = deos_df.fillna('')
        provisions_df = provisions_df.fillna('')
        
        _data_cache = {
            'services': services_df,
            'bsks': bsks_df,
            'deos': deos_df,
            'provisions': provisions_df
        }
        
        logger.info(f"✅ Loaded {len(services_df)} services, {len(bsks_df)} BSKs, "
                   f"{len(deos_df)} DEOs, {len(provisions_df)} provisions")
        
        return _data_cache
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data: {e}")
        import traceback
        traceback.print_exc()
        return None

# ... (rest of the functions stay the same)