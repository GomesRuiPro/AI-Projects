import torch.nn as nn
import torch.optim as optim
import torch.hub as hub
import numpy as np
from torchvision import transforms
from torchvision.models.video import r3d_18, R3D_18_Weights, r2plus1d_18, R2Plus1D_18_Weights
from torch.utils.data import Dataset, DataLoader
from torch.amp import autocast, GradScaler
import cv2
from tools.utilities import Utility
import time
from abc import ABC, abstractmethod
from tools.models.object.factory import YoloFactory, DetectorFactory
from tools.models.genre.factory import PytorchVideoFactory

VLM_CONFIG = Utility.load_yaml()["vlm"]

class VLMGaming():

    extract_features_models = []

    def __init__(self):
       pass

    def start_model(self, with_object=False, with_environment=False, with_movement=False, with_genre=False):
        object_detection_model = ObjectDetection.create() if with_object else None
        environment_model = Environment.create() if with_environment else None
        movement_model = Movement.create() if with_movement else None
        genre_model = Genre.create() if with_genre else None
        self.extract_features_models.extend([m for m in [object_detection_model, environment_model, movement_model, genre_model] if m is not None])
        
    def get_model(self, model_type):
        for extract_features_model in self.extract_features_models:
            if Utility.is_object_instance_of(extract_features_model, model_type):
                return extract_features_model 

        return None

    def get_models(self):
        return self.extract_features_models
    
    def get_genre(self, video_path):
        model = self.get_model("Genre")
        output = model.execute()
        return output



    def execute(self, video_path):
        result = []
        for extract_features_model in self.extract_features_models:
            features = extract_features_model.execute(video_path)
            result.extend({
                'model': extract_features_model.name,
                'features': features
            })
        return result

    def _get_probability_percentage(value):
        return int(round(value, 2) * 100)
    
    def get_predicted_genres(self):
        return self.predicted_genres
    
    # Matching the probability value with the label depends on the index value of each list
    def set_predicted_genres(self, predicted_probabilities):
        for idx, predicted_probability in enumerate(predicted_probabilities):
            self.predicted_genres.append((VLMGaming.genreDataset.labels[idx][0], VLMGaming._get_probability_percentage(float(predicted_probability.item())))) # Note: 0 represent the label_name and 1 the label_idx

    def predict_game_genre(self, video_filename_path):
        self.predicted_genres = []


    # @staticmethod
    # def extract_features(clip):
    #     # Remove the final classification layer to get features
    #     modules = list(VLMGaming.model.children())[:-1]
    #     feature_extractor = torch.nn.Sequential(*modules)

    #     with torch.no_grad():
    #         features = feature_extractor(clip)
    #     return features.squeeze()

class Movement():
    model = None

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['movement']
        movementFactory = None

        # if 'yolo' in config['name']:
        #     objectFactory = YoloFactory(config)
        # elif 'detector' in config['name']:
        #     objectFactory = DetectorFactory(config)
        # else:
        return None

        Movement.model = movementFactory.create(pretrained=VLM_CONFIG['use_model_finetuned'], is_local=config['is_local'])
        return Movement.model

    def execute(video_path):
        Movement.model.execute()

class ObjectDetection():
    model = None

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['object']
        objectFactory = None

        if 'yolo' in config['name']:
            objectFactory = YoloFactory(config)
        elif 'detector' in config['name']:
            objectFactory = DetectorFactory(config)
        else:
            return None

        ObjectDetection.model = objectFactory.create(pretrained=VLM_CONFIG['use_model_finetuned'], is_local=config['is_local'])
        return ObjectDetection.model

    def execute(video_path):
        ObjectDetection.model.execute()

class Genre():
    model = None

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['genre']
        genreFactory = None

        if 'x3d' in config['name']:
            genreFactory = PytorchVideoFactory(config)
        else:
            return None

        Genre.model = genreFactory.create(pretrained=VLM_CONFIG['use_model_finetuned'], is_local=config['is_local'])
        return Genre.model

    def execute(video_path):
        Genre.model.execute()

class Environment():
    model = None

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['environment']
        environmentFactory = None

        # if 'yolo' in config['name']:
        #     objectFactory = YoloFactory(config)
        # elif 'detector' in config['name']:
        #     objectFactory = DetectorFactory(config)
        # else:
        return None

        Environment.model = environmentFactory.create(pretrained=VLM_CONFIG['use_model_finetuned'], is_local=config['is_local'])
        return Environment.model

    def execute(video_path):
        Environment.model.execute()
