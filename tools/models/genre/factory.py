import torch
import cv2
from abc import ABC, abstractmethod
import torch.hub as hub
from tools.models.genre.entities.pytorchvideo import PytorchVideo

class GenreFactory(ABC):
    config = None

    def __init__(self, config):
            self.config = config

    @abstractmethod
    def create(self, pretrained=True, is_local=False):
        pass

class PytorchVideoFactory(GenreFactory):
    
    def __init__(self, config):
        super().__init__(config)

    def create(self, pretrained=True, is_local=False):
        return PytorchVideo(self.config['name'], self.config['version'], pretrained=pretrained, is_local=is_local)