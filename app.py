import webview
from services import SerialManager, ConfigService, ImageService, FileTransferService, LabelService, DataService
from models import ButtonConfig
from ui import EelInterface
import threading as th

from pathlib import Path

class WorkflowBuddy:
    def __init__(self):
        self.paths = self._get_paths()
        self.config = ConfigService(self.paths['config'])
        self.images = ImageService(self.paths['images'])
        self.labels = LabelService(self.paths['labels'])
        self.data = DataService(self.config, self.images, self.labels)

        self.serial_manager = SerialManager(self.data)

        self.button_config = ButtonConfig()
        self.file_transfer = FileTransferService(self.serial_manager)

        self.ui = EelInterface(self.config, 
                               self.serial_manager, 
                               self.images, 
                               self.labels, 
                               self.data, 
                               self.button_config, 
                               self.file_transfer,
                               self.paths['web'])
        
        self.event_loop = None

    def _get_paths(self):
        """Get application paths"""
        import sys
        import os
        
        if getattr(sys, 'frozen', False):
            app_path = Path(sys._MEIPASS)
        else:
            app_path = Path(__file__).parent
        
        if sys.platform == "win32":
            user_data = Path(os.getenv('LOCALAPPDATA')) / 'WorkflowBuddyReworked'
        elif sys.platform == "darwin":
            user_data = Path.home() / 'Library' / 'Application Support' / 'WorkflowBuddyReworked'
        else:
            user_data = Path.home() / '.local' / 'share' / 'workflowbuddyreworked'
        
        user_data.mkdir(parents=True, exist_ok=True)
        
        return {
            'app': app_path,
            'web': app_path / 'web',
            'config': user_data / 'config.json',
            'images': user_data / 'images',
            'labels': user_data / 'labels'
        }
    
    def run(self):
        """Run application"""
        eel_thread = th.Thread(
            target=lambda: self.ui.start(mode=None, block=True),
            daemon=True
        )
        eel_thread.start()
        
        win = webview.create_window(
            title="WorkflowBuddy",
            url="http://localhost:8888",
            width=640,
            height=480,
            resizable=False,
            fullscreen=False,
            text_select=False
        )
        webview.start()

if __name__ == '__main__':
    app = WorkflowBuddy()
    app.run()