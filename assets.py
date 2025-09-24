import zipfile
import os

from utils import ASSETS_ZIP_PATH, TEMP_ASSETS_DIR
from utils import debug_print

def extract_video():
    """Extract the intro video before extracting other files"""
    with zipfile.ZipFile(ASSETS_ZIP_PATH, 'r') as zip_ref:
        # Extract only the intro video first
        zip_ref.extract("videos/FreeRadsLogoFading.mp4", TEMP_ASSETS_DIR)
        debug_print(f"Intro video extracted to {TEMP_ASSETS_DIR}")

def extract_assets():
    """Extract songs from the zip file to a temporary directory"""
    if not os.path.exists(TEMP_ASSETS_DIR):
        os.makedirs(TEMP_ASSETS_DIR)
    
    with zipfile.ZipFile(ASSETS_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(TEMP_ASSETS_DIR)
        debug_print(f"Assets extracted to {TEMP_ASSETS_DIR}")