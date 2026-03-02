from typing import Optional, Dict
from pathlib import Path
import sys
import os

class LabelService:
    def __init__(self, labels_path: Optional[str] = None):
        if labels_path is None:
            self.labels_path = self._get_default_labels_path()
        else:
            self.labels_path = labels_path

        self._ensure_labels_exists()
    
    def _get_default_labels_path(self) -> Path:
        if sys.platform == "win32":
            base = Path(os.getenv('LOCALAPPDATA'))
        elif sys.platform == "darwin":
            base = Path.home() / 'Library' / 'Application Support'
        else:
            base = Path.home() / '.local' / 'share'

        labels_dir = base / 'WorkflowBuddyReworked' / 'labels'
        labels_dir.mkdir(parents=True, exist_ok=True)
        return labels_dir
    
    def _ensure_labels_exists(self):
        if not Path.exists(self.labels_path):
            print(f"Labels path doesn't exist, creating.")
            Path.mkdir(self.labels_path, exist_ok=True)

    def load(self) -> Dict:
        try:
            labels_list = [
                f.name for f in self.labels_path.iterdir() if f.is_file() and f.suffix.lower()==".txt"
            ]
            return labels_list
        except Exception as e:
            print(f"Labels loading failed: {e}")

    def load_paths(self) -> Dict:
        try:
            labels_list = {
                f.name.removesuffix(".txt"): str(f.absolute()) for f in self.labels_path.iterdir() if f.is_file() and f.suffix.lower()==".txt"
            }
            return labels_list
        except Exception as e:
            print(f"Labels loading failed: {e}")

    def get_label_for_button(self, button_id: str) -> str:
        try:
            with open(Path(self.labels_path) / Path(button_id).with_suffix(".txt"), "r") as f:
                data = f.readline()
                f.close()
            return data
        except Exception as e:
            print(f"Failed to get label: {e}")

    
    def save(self,  button_id: str, label: str) -> bool:
        """Save label"""
        try:
            with open(Path(self.labels_path) / Path(button_id).with_suffix(".txt"), "w") as f:
                f.write(label)
                f.close()
            return True
        except Exception as e:
            print(f"Failed to save label: {e}")
            return False
    
    def delete_label(self, button_id: str) -> bool:
        """Delete label"""
        try:
            os.remove(Path(self.labels_path) / Path(button_id).with_suffix(".txt"))
            return True
        except Exception as e:
            print(f"Label deletion failed: {e}")
            return False