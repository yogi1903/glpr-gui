# src/config.py

import json
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    # Get the directory of the current file (config.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    
    config_path = os.path.join(project_root, 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Convert relative paths to absolute paths
        config['stylesheet_path'] = os.path.abspath(os.path.join(project_root, 'assets', 'styles', 'stylesheet.qss'))
        config['database_file'] = os.path.abspath(os.path.join(project_root, 'license_plates.db'))
        config['models']['license_plate'] = os.path.abspath(os.path.join(project_root, 'models', 'bestbest.pt'))
        config['images']['gitam_logo'] = os.path.abspath(os.path.join(project_root, 'assets', 'images', 'gitam_logo_green.jpeg'))
        config['images']['navy_logo'] = os.path.abspath(os.path.join(project_root, 'assets', 'images', 'indian_navy_logo.png'))
        config['captured_images_dir'] = os.path.abspath(os.path.join(project_root, 'captured_images'))
        
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in configuration file: {config_path}")