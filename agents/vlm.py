import torch
import cv2
from innovation.FeedbackerAi.tools.local.utilities import Utility
import time
import numpy as np
from abc import ABC, abstractmethod
from innovation.FeedbackerAi.agents.tools_client import ToolsClient
from innovation.FeedbackerAi.tools.models.model import VideoFeatureModel, VideoModel, Model
from innovation.FeedbackerAi.agents.agent import Agent
from innovation.FeedbackerAi.agents.tools_client import Operation, ExecutionMode, ComponentType
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend
from innovation.FeedbackerAi.tools.local.logger.logger import LoggerFactory, LoggerSingleton

VLM_CONFIG = Utility.load_yaml()["vlm"]

class VLMGaming(Agent):

    clip_duration_seconds = None
    num_frames_to_read = None

    def __init__(self, workflow_config):
        super().__init__(workflow_config, VLM_CONFIG)
        self.video_frames = []
        
    def validate_video_loaded(func):
        def wrapper(self, *args, **kwargs):
            if not self.video_frames:
                raise Exception(f"The method {func.__name__} was called before having the video loaded")
            return func(self, *args, **kwargs)
        return wrapper


    # def start_model(self, *with_features):
    #     self.models = {
    #         "object": None,
    #         "environment": None,
    #         "movement": None,
    #         "video_classification": None,
    #     }

    #     for with_feature in with_features:
    #         if with_feature == "with_object":
    #             self.models["object"] = ObjectDetection.create()
    #         elif with_feature == "with_environment":
    #             self.models["environment"] = Environment.create()
    #         elif with_feature == "with_movement":
    #             self.models["movement"] = Movement.create()
    #         elif with_feature == "with_video_classification":
    #             self.models["video_classification"] = VideoClassification.create()

    # def get_extract_features_models(self):
    #     self.tools_client.create(Operation.)
    #     extract_features_models = []
    #     for name, model in self.models.items():
    #         if isinstance(model, VideoFeatureModel):
    #             extract_features_models.append(model)
    #     return extract_features_models

    def load_video(self, video_converted_path):
        # Read the video using OpenCV
        if not Utility.does_file_exist(video_converted_path):
            raise Exception(f"File {video_converted_path} does not exist!")
        cap = cv2.VideoCapture(video_converted_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video file: {video_converted_path}")
        current_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if current_total_frames == 0:
            raise Exception(
                f"Failed to read the video '{video_converted_path}'")

        # num_frames vs clip duration
        current_clip_duration_seconds = int(round(current_total_frames/fps))

        clip_duration_seconds = current_clip_duration_seconds
        num_frames_to_read = current_total_frames
        # Filter by num of frames
        if VLM_CONFIG['max_num_frames']:
            num_frames_to_read = VLM_CONFIG['max_num_frames']
        # Filter by duration
        if VLM_CONFIG['clip_duration_seconds']:
            clip_duration_seconds = VLM_CONFIG['clip_duration_seconds']

        # Prioritize clip duration. If higher than max allowed, check number of frames. If higher than allowed, use max.
        if VLM_CONFIG['max_num_frames'] and VLM_CONFIG['clip_duration_seconds']:
            if current_total_frames > num_frames_to_read:
                clip_duration_seconds = current_clip_duration_seconds
            else:
                num_frames_to_read = current_total_frames
        
        VLMGaming.clip_duration_seconds = clip_duration_seconds
        VLMGaming.num_frames_to_read = num_frames_to_read

        frame_indices = np.linspace(
            0, current_total_frames - 1, num_frames_to_read, dtype=int)

        frames = []
        key_pressed = None
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                if VLM_CONFIG['device_debug'] and not (key_pressed == ord('q')):
                    Utility.log(f"Frame shape: {frame.shape}")
                    Utility.log(f"Pixel at (0,0): {frame[0,0]}")
                    # if LoggerFactory.is_debug():
                    cv2.imshow('Frame', frame)
                    key_pressed = cv2.waitKey(1000)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Correct order
                frame = torch.from_numpy(frame).float()  # shape: H x W x C
                frame = frame.permute(2, 0, 1)  # shape: C x H x W
                frames.append(frame)
            else:
                break
        cv2.destroyAllWindows()
        cap.release()
        
        self.video_frames = frames

    @validate_video_loaded
    @Agent.to_fallback(Operation.EXTRACT_GENRE, ComponentType.MODEL)
    def extract_genre(self):
        
        model = self.components[0]
        model.set_video(self.video_frames)
        return model.execute()
    
    @validate_video_loaded
    @Agent.to_fallback(Operation.EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES, ComponentType.MODEL)
    def extract_object_features(self, trends: Set[Trend]):

        models_answers: List[str] = []
        for model in self.components:
            
            # These have to passed after the model was created by the tools client because they are updated after reading the video
            model.num_frames_to_read = VLMGaming.num_frames_to_read
            model.clip_duration_seconds = VLMGaming.clip_duration_seconds
            trends_features_types = set()
            for trend in trends:
                trends_features_types.add(trend.feature_type.description)
            model.class_names = list(trends_features_types)
            answers = model.execute(self.video_frames)
            
            if not answers:
                continue
                    
            models_answers.extends(answers)
                
        return models_answers

    # def execute(self, video_path):
    #     result = []

    #     video_frames = self.__load_video(video_path)
    #     extract_features_models = self.get_extract_features_models()

    #     for extract_features_model in extract_features_models:
    #         extract_features_model.set_video(video_frames)
    #         features = extract_features_model.execute(
    #             VLMGaming.num_frames_to_read, VLMGaming.clip_duration_seconds)
    #         result.append({
    #             'model': extract_features_model.model_name,
    #             'features': features
    #         })
    #     return result
