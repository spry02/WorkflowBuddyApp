from typing import Optional, Dict
from pathlib import Path
import sys
import os
import json

class ConfigService:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            self.config_path = self._get_default_config_path()
        else:
            self.config_path = config_path

        self._ensure_config_exists()
    
    def _get_default_config_path(self) -> Path:
        if sys.platform == "win32":
            base = Path(os.getenv('LOCALAPPDATA'))
        elif sys.platform == "darwin":
            base = Path.home() / 'Library' / 'Application Support'
        else:
            base = Path.home() / '.local' / 'share'

        config_dir = base / 'WorkflowBuddyReworked'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'
    
    def _ensure_config_exists(self):
        if not Path.exists(self.config_path):
            print(f"Config path doesn't exist, creating.")
            # Path.mkdir(self.config_path, exist_ok=True)
            Path.write_text(self.config_path, data='''{}''')

    def load(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save(self, config: Dict) -> bool:
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Config save failed: {e}")
            return False
        
    def get_item(self, button_id: str) -> Dict:
        return self.load().get(button_id, {})