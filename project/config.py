import json
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Convert relative paths to absolute paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config['stylesheet_path'] = os.path.join(base_dir, config['stylesheet_path'])
        config['images']['gitam_logo'] = os.path.join(base_dir, config['images']['gitam_logo'])
        config['images']['navy_logo'] = os.path.join(base_dir, config['images']['navy_logo'])
        
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in configuration file: {config_path}")