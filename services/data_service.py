from services import ConfigService, ImageService, LabelService

class DataService:
    def __init__(self, config_service: ConfigService, image_service: ImageService, label_service: LabelService):
        self.config = config_service
        self.image = image_service
        self.label = label_service

    def get_item_data(self, button_id: str):
        config_data = self.config.get_item(button_id)
        image_data = self.image.get_image_path(button_id)
        label_data = self.label.get_label_for_button(button_id)

    def get_full_data(self):
        config = self.config.load()
        images = self.image.load_paths()
        labels = self.label.load_paths()
        return config, images, labels