import torch
import cv2
from innovation.FeedbackerAi.tools.local.utilities import Utility
import time
import numpy as np
from abc import ABC, abstractmethod
from innovation.FeedbackerAi.agents.tools_client import ToolsClient
from innovation.FeedbackerAi.tools.models.model import VideoFeatureModel, VideoModel, Model
from innovation.FeedbackerAi.agents.agent import Agent
from innovation.FeedbackerAi.agents.tools_client import Operation, ExecutionMode
from typing import Optional, Dict, Any, List

VLM_CONFIG = Utility.load_yaml()["vlm"]

class VLMGaming(Agent):

    clip_duration_seconds = None
    num_frames_to_read = None

    def __init__(self, workflow_config):
        super().__init__(workflow_config, VLM_CONFIG)

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
                if VLM_CONFIG['device_debug']:
                    print("Frame shape:", frame.shape)
                    print("Pixel at (0,0):", frame[0,0])
                    cv2.imshow('Frame', frame)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Correct order
                frame = torch.from_numpy(frame).float()  # shape: H x W x C
                frame = frame.permute(2, 0, 1)  # shape: C x H x W
                frames.append(frame)
            else:
                break
        cap.release()

        return frames

    def extract_genre(self, video_path):
        self.tools_client.create(Operation.EXTRACT_GENRE)
        model_execution_mode = self.tools_client.models["execution_mode"]
        models = self.tools_client.models["entities"]

        if not models:
            return None
                
        model = models[0]
        if model_execution_mode == ExecutionMode.FALLBACK:
            return model.execute()
        
        video_frames = self.__load_video(video_path)
        model.set_video(video_frames)
        return model.execute()
    
    def extract_object_features(self, video_path, text_prompts):
        self.tools_client.create(Operation.EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES)
        models_execution_mode = self.tools_client.models["execution_mode"]
        models = self.tools_client.models["entities"]

        if not models:
            return None
        
        if models_execution_mode == ExecutionMode.FALLBACK:
            return models[0].execute()

        models_answers: List[str] = []
        video_frames = self.__load_video(video_path)
        for model in models:
            
            # These have to passed after the model was created by the tools client because they are updated after reading the video
            model.num_frames_to_read = VLMGaming.num_frames_to_read
            model.clip_duration_seconds = VLMGaming.clip_duration_seconds
            answers = model.execute((video_frames, text_prompts)) 
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
