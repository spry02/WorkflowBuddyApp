from typing import Optional
from pathlib import Path
import sys
import os
from PIL import Image
import base64
from io import BytesIO
import numpy as np

class ImageService:
    def __init__(self, images_path: Optional[str] = None):
        if images_path is None:
            self.images_path = self._get_default_images_path()
        else:
            self.images_path = images_path

        self._ensure_images_exists()
    
    def _get_default_images_path(self) -> Path:
        if sys.platform == "win32":
            base = Path(os.getenv('LOCALAPPDATA'))
        elif sys.platform == "darwin":
            base = Path.home() / 'Library' / 'Application Support'
        else:
            base = Path.home() / '.local' / 'share'

        images_dir = base / 'WorkflowBuddyReworked' / 'images'
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir
    
    def _ensure_images_exists(self):
        if not Path.exists(self.images_path):
            print(f"Config path doesn't exist, creating.")
            Path.mkdir(self.images_path, exist_ok=True)

    def load(self) -> list:
        try:
            extensions = ('.png', '.jpg', '.jpeg', '.bmp')
            images_list = [
                f.name for f in self.images_path.iterdir() if f.is_file() and f.suffix.lower() in extensions
            ]
            return images_list
        except Exception as e:
            print(f"Images loading failed: {e}")

    def load_paths(self) -> list:
        try:
            extensions = ('.png', '.jpg', '.jpeg', '.bmp')
            images_list = {
                f.name.removesuffix(".jpg"): str(f.absolute()) for f in self.images_path.iterdir() if f.is_file() and f.suffix.lower() in extensions
            }
            return images_list
        except Exception as e:
            print(f"Images loading failed: {e}")
    
    def get_image_path(self, button_id) -> Path:
        if Path.exists(self.images_path / Path(button_id).with_suffix(".jpg")):
            return Path(self.images_path) / Path(button_id).with_suffix(".jpg")
    
    def save(self, button_id: str, image_path: str) -> bool:
        """Save image"""
        try:
            img = Image.open(image_path)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
                img.resize((96,96))
            img.save(Path(self.images_path) / Path(button_id).with_suffix(".jpg"))
            return True
        except Exception as e:
            print(f"Image save failed: {e}")
            return False
        
    def save_from_b64(self, button_id: str, image:str):
        try:
            _, encoded = image.split(',', 1)
            image_data_decoded = base64.b64decode(encoded)

            rgba = np.array(Image.open(BytesIO(image_data_decoded)))

            rgba[rgba[...,-1]==0] = [255,255,255,255]

            img = Image.fromarray(rgba)

            img = img.resize((96, 96), Image.Resampling.LANCZOS)
            img.convert("RGB").save(Path(self.images_path)/Path(button_id).with_suffix(".jpg"), "JPEG", quality=100)
        except Exception as e:
            print(f"Error while saving from b64: {e}")
    
    def delete_image(self, button_id: str) -> bool:
        """Delete image"""
        try:
            os.remove(Path(self.images_path) / Path(button_id).with_suffix(".jpg"))
            return True
        except Exception as e:
            print(f"Image deletion failed: {e}")
            return False
        
    def load_b64_image(self, image_path: str):
        try:
            if not os.path.exists(image_path):
                return None
            
            with open(image_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
            
            return f'data:image/jpg;base64,{encoded}'
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None