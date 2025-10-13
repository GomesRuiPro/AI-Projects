import torch
import cv2
from tools.utilities import Utility
import time
import numpy as np
from abc import ABC, abstractmethod
from tools.models.model import VideoFeatureModel, VideoModel, Model
from tools.models.factory import EnvironmentFactory, MovementFactory, VideoClassificationFactory, ObjectFactory

APIS_CONFIG = Utility.load_yaml()["apis"]
VLM_CONFIG = Utility.load_yaml()["vlm"]


class VLMGaming():

    models = []
    clip_duration_seconds = None
    num_frames_to_read = None

    def __init__(self):
        pass

    def start_model(self, with_object=False, with_environment=False, with_movement=False, with_video_classification=False):
        object_detection_model = ObjectDetection.create() if with_object else None
        environment_model = Environment.create() if with_environment else None
        movement_model = Movement.create() if with_movement else None
        video_classification_model = VideoClassification.create(
        ) if with_video_classification else None
        self.models = {'object': object_detection_model, 'movement': movement_model,
                       'environment': environment_model, 'video_classification': video_classification_model}

    def get_model(self, model_type):
        return self.models[model_type]

    def get_models(self):
        return self.models

    def get_extract_features_models(self):
        extract_features_models = []
        for name, model in self.models.items():
            if isinstance(model, VideoFeatureModel):
                extract_features_models.append(model)
        return extract_features_models

    def __load_video(self, video_converted_path):
        # Read the video using OpenCV
        if not Utility.does_file_exist(video_converted_path):
            raise Exception(f"File {video_converted_path} does not exist!")
        cap = cv2.VideoCapture(video_converted_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video file: {video_converted_path}")
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if total_frames == 0:
            raise Exception(
                f"Failed to read the video '{video_converted_path}'")

        # num_frames vs clip duration
        max_num_frames = VLM_CONFIG['max_num_frames']
        clip_duration_seconds = VLM_CONFIG['clip_duration_seconds']
        num_frames_to_read = max_num_frames

        # Prioritize clip duration. If higher than max allowed, check number of frames. If higher than allowed, use max.
        if total_frames / fps > clip_duration_seconds:
            num_frames_to_read = clip_duration_seconds * fps
            if num_frames_to_read > max_num_frames:
                num_frames_to_read = max_num_frames
        else:
            clip_duration_seconds = int(round(total_frames/fps))

        VLMGaming.clip_duration_seconds = clip_duration_seconds
        VLMGaming.num_frames_to_read = num_frames_to_read

        frame_indices = np.linspace(
            0, total_frames - 1, num_frames_to_read, dtype=int)

        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # if VLM_CONFIG['device_debug']:
                #     print("Frame shape:", frame.shape)
                #     print("Pixel at (0,0):", frame[0,0])
                #     cv2.imshow('Frame', frame)
                #     cv2.waitKey(0)
                #     cv2.destroyAllWindows()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Correct order
                frame = torch.from_numpy(frame).float()  # shape: H x W x C
                frame = frame.permute(2, 0, 1)  # shape: C x H x W
                frames.append(frame)
            else:
                break
        cap.release()

        return frames

    def get_genre(self, video_path):
        model = self.get_model("video_classification")

        if isinstance(model, VideoModel):
            video_frames = self.__load_video(video_path)
            model.set_video(video_frames)

        return model.execute()

    def execute(self, video_path):
        result = []

        video_frames = self.__load_video(video_path)
        extract_features_models = self.get_extract_features_models()

        for extract_features_model in extract_features_models:
            extract_features_model.set_video(video_frames)
            features = extract_features_model.execute(
                VLMGaming.num_frames_to_read, VLMGaming.clip_duration_seconds)
            result.append({
                'model': extract_features_model.model_name,
                'features': features
            })
        return result


class ModelClient(ABC):

    model = None

    @abstractmethod
    def create():
        pass


class Movement(ModelClient):

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['movement']


class ObjectDetection(ModelClient):

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['object']
        objectFactory = ObjectFactory(
            config, APIS_CONFIG['hugging_face']['token'])
        ModelClient.model = objectFactory.create(
            VLM_CONFIG['device_type'], VLM_CONFIG['use_model_finetuned'], VLM_CONFIG['device_debug'])
        return ModelClient.model


class Environment(ModelClient):

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['environment']


class VideoClassification(ModelClient):

    @staticmethod
    def create():
        config = VLM_CONFIG['models']['video_classification']
        videoClassificationFactory = VideoClassificationFactory(config)
        ModelClient.model = videoClassificationFactory.create(
            VLM_CONFIG['device_type'], VLM_CONFIG['use_model_finetuned'], VLM_CONFIG['device_debug'])
        return ModelClient.model
