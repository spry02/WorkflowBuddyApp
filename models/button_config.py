from typing import Optional
from enum import Enum
from pathlib import Path
from services import DataService
import pyautogui
import os
import time
import keyboard

class ActionType(Enum):
    """Typy akcji przycisku"""
    SHORTCUT = "shortcut" 
    TEXT = "txt"          
    PROGRAM = "program"    
    NONE = "none"          
    
    @classmethod
    def from_string(cls, value: str) -> 'ActionType':
        """Stwórz ActionType ze stringa"""
        try:
            return cls(value.lower())
        except ValueError:
            print(f"Unknown action type: {value}, defaulting to NONE")
            return cls.NONE
    
    def __str__(self) -> str:
        return self.value

class ButtonConfig:
    def __init__(self, button_id: Optional[str] = None, label: Optional[str] = None, image: Optional[str] = None, action_type: ActionType = ActionType.NONE, action_data: Optional[str] = None, data_service: Optional[DataService] = None):
        self.button_id: Optional[str] = button_id
        self.label: Optional[str] = label
        self.image: Optional[str] = image
        self.action_type: ActionType = action_type
        self.action_data: Optional[str] = action_data
        self.data = data_service

    def get_from_config(self):
        if self.button_id is not None:
            temp_data = self.data.config.get_item(self.button_id)
            try:
                self.action_type = ActionType.from_string(temp_data["action_type"])
                self.action_data = temp_data['action_data'] or None
                self.label = self.data.label.get_label_for_button(self.button_id)
                self.image_path = self.data.image.get_image_path(self.button_id)
            except Exception as e:
                print(f"Error while loading config: {e}")

    def set_default_button(self):
        if self.button_id is not None:
            current_configuration = self.data.config.load()
            current_configuration[self.button_id] = {
                "action_type": "txt",
                "action_data": "HELLO"
                }
            self.data.config.save(current_configuration)
            self.data.label.save(self.button_id, "TESTOWA")
            self.data.image.save(self.button_id, "C:\\Users\\plspry\\AppData\\Local\\WorkflowBuddyReworked\\images\\btn1-1.jpg")

    def set_button_config(self):
        if self.button_id is not None:
            current_configuration = self.data.config.load()
            if self.button_id not in current_configuration:
                current_configuration[self.button_id] = {
                    "action_type": self.action_type,
                    "action_data": self.action_data
                }
            else:
                current_configuration[self.button_id]['action_type'] = self.action_type
                current_configuration[self.button_id]['action_data'] = self.action_data
            if self.image is not None:
                self.data.image.save_from_b64(self.button_id, self.image)
            if self.label is not None:
                self.data.label.save(self.button_id, self.label) 
            self.data.config.save(current_configuration)

    def clear_button(self):
        if self.button_id is not None:
            current_configuration = self.data.config.load()
            try:
                current_configuration.pop(self.button_id)
            except:
                pass
            self.data.config.save(current_configuration)
            self.data.label.delete_label(self.button_id)
            self.data.image.delete_image(self.button_id)

    def clear_all_buttons(self, buttons_list: list):
        current_configuration = self.data.config.load()
        for i in buttons_list:
            try:
                current_configuration.pop(i)
            except:
                pass
            
            self.data.label.delete_label(i)
            self.data.image.delete_image(i)
    
    def __str__(self):
        if self.button_id is not None:
            return (f"Button {self.button_id}, label: {self.label}, image path: {self.image_path}, action type: {self.action_type}, action data: {self.action_data}")
    
class ButtonClass(ButtonConfig):
    def __init__(self, button_id: Optional[str] = None, label: Optional[str] = None, image_path: Optional[Path] = None, action_type: ActionType = ActionType.NONE, action_data: Optional[str] = None, data_service: Optional[DataService] = None):
        super().__init__(button_id, label, image_path, action_type, action_data, data_service)

    def execute(self):
        if self.button_id is not None:
            temp_data = self.data.config.get_item(self.button_id)
            try:
                self.action_type = ActionType.from_string(temp_data.get('action_type', None))
                self.action_data = temp_data.get('action_data', None)
                if self.action_type is not ActionType.NONE and self.action_data is not None:
                    if self.action_type == ActionType.SHORTCUT:
                        self.shortcut_execute()
                    elif self.action_type == ActionType.TEXT:
                        self.text_write()
                    elif self.action_type == ActionType.PROGRAM:
                        self.program_execute()
            except Exception as e:
                print(f"Error while executing: {e}")

        del self

    def shortcut_execute(self) -> bool:
        try:
            shortcut = self.action_data.split(" ")
            pyautogui.shortcut(shortcut)
            return True
        except Exception as e:
            print(f"Error while executing shortcut button: {e}")
            return False
        
    def text_write(self) -> bool:
        try:
            time.sleep(.2)
            keyboard.write(self.action_data, delay=.01)
            return True
        except Exception as e:
            print(f"Error while executing text button: {e}")
            return False
        
    def program_execute(self) -> bool:
        try:
            if Path.exists(Path(self.action_data)):
                os.startfile(Path(self.action_data))
            else:
                os.system(self.action_data)
            return True
        except Exception as e:
            print(f"Error while executing program button: {e}")
            return False