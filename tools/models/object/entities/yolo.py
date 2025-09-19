from ultralytics import YOLO
import torch.hub as hub
from tools.models.object.entities.model import Model

class Yolo(Model):
        
    def __init__(self, model_name='yolo', model_version='v5s', pretrained=True, is_local=False):
        super().__init__(model_name, model_version, pretrained, is_local)
        if is_local:
            self.model = YOLO(model_name+model_version)
        else:
            root_repository = "ultralytics/"
            repository_name = root_repository+model_name+model_version[:-1]
            self.model = hub.load(repository_name, model_name+model_version, pretrained=pretrained)  # Make sure the model is available in pytorch repository

    def execute(self, video_path):
        pass    
