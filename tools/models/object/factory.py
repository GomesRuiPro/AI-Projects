import torch
from ultralytics import YOLO
import cv2
from abc import ABC, abstractmethod
from tools.models.object.entities.yolo import Yolo

class ObjectFactory(ABC):
    config = None

    def __init__(self, config):
            self.config = config

    @abstractmethod
    def create(self, pretrained=True, is_local=False):
        pass

class YoloFactory(ObjectFactory):
    
    def __init__(self, config):
        super().__init__(config)

    def create(self, pretrained=True, is_local=False):
        return Yolo(self.config['name'], self.config['version'], pretrained=pretrained, is_local=is_local)

class DetectorFactory(ObjectFactory):

    def __init__(self, config):
        super().__init__(config)

    def create(self, pretrained=True, is_local=False):
        return None