import eel
from pathlib import Path
from typing import Optional

from services import SerialManager, ConfigService, ImageService, FileTransferService, LabelService, DataService
from models import ButtonConfig

class EelInterface:
    def __init__(self,
                 config: ConfigService,
                 serial: SerialManager,
                 image: ImageService,
                 label: LabelService,
                 data: DataService,
                 button_config: ButtonConfig,
                 file_transfer: FileTransferService,
                 web_path: str = 'web',
                 host: str = 'localhost',
                 port: int = 8888,
                 ):
        self.config = config
        self.serial = serial
        self.image = image
        self.label = label
        self.data = data

        self.web_path = web_path
        self.host = host
        self.port = port

        self.file_transfer = file_transfer
        self.button_config = button_config

        eel.init(self.web_path)

        self._register_eel_functions()

    def _register_eel_functions(self):
        @eel.expose
        def get_connection_status():
            return {
                'status': self.serial.status,
                'port': self.serial.port if self.serial else None
            }

        @eel.expose
        def load_b64(image_path: str):
            return self.image.load_b64_image(image_path)
        
        @eel.expose
        def load_label(button_id: str):
            return self.label.get_label_for_button(button_id)

        @eel.expose
        def _transfer_file(command: str, data_path: str):
            self.file_transfer._writer(command, data_path)

        @eel.expose
        def close_connection():
            self.serial.disconnect()
        
        @eel.expose
        def reconnect():
            self.serial.find_esp()
        
        @eel.expose
        def get_config():
            return self.data.get_full_data()
        
        @eel.expose
        def clear_button(button_id: str):
            button = ButtonConfig(button_id, data_service=self.data)
            self.file_transfer.clear_button(button_id)
            button.clear_button()

        @eel.expose
        def overwrite_config():
            button = ButtonConfig(data_service=self.data)
            self.file_transfer.clear_all_buttons()

            buttons_list = [k for k in button.data.config.load().keys()]

            print(buttons_list)


            for button_id in buttons_list:
                try:
                    self.file_transfer._writer('file', Path(self.image.images_path)/Path(button_id).with_suffix(".jpg"))
                except Exception as e:
                    print(f"Failed to send image: {e}")
                try:
                    self.file_transfer._writer('file', Path(self.label.labels_path)/Path(button_id).with_suffix(".txt"))
                except Exception as e:
                    print(f"Failed to send label: {e}")
            
            
        
        @eel.expose
        def save_button(button_id: str, action_type: str, action_data: str, label: str = None, image: str = None):
            button = ButtonConfig(button_id, 
                                  label=label, 
                                  image=image, 
                                  action_type=action_type, 
                                  action_data=action_data, 
                                  data_service=self.data)
            button.set_button_config()
            self.file_transfer._writer('file', Path(self.image.images_path)/Path(button_id).with_suffix(".jpg"))
            self.file_transfer._writer('file', Path(self.label.labels_path)/Path(button_id).with_suffix(".txt"))

        @eel.expose
        def get_images():
            return self.image.load()
        
    def start(self, mode: Optional[str] = None, block: bool = True):
        try:
            eel.start('index.html', mode=mode, host=self.host, port=self.port, block=block)
        except Exception as e:
            print(f"Error occured while starting eel: {e}")
            raise