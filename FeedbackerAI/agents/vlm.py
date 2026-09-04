from collections import Counter
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
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend
from innovation.FeedbackerAi.tools.models.entities.model import ModelAnswer, ModelQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion, TextAnswer
from innovation.FeedbackerAi.tools.models.entities.video import VideoQuestion, VideoAnswer
from innovation.FeedbackerAi.tools.models.client import ModelClient
from innovation.FeedbackerAi.tools.local.memory.db import DB

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
    def extract_genre(self) -> ModelAnswer:
        
        videoQuestion = VideoQuestion(video_frames=self.video_frames, text="classify")
        videoQuestion.metadata["content"] = [member.name for member in GENRE]
        videoQuestion.metadata["num_frames_to_read"] = VLMGaming.num_frames_to_read
        videoQuestion.metadata["clip_duration_seconds"] = VLMGaming.clip_duration_seconds
        videoAnswers = super().component_intersect_results_fn(videoQuestion, ModelClient.run_model)
        labels = [videoAnswer.metadata['label'] for videoAnswer in videoAnswers]
        most_common_genre = Counter(labels).most_common(1)
        answer: ModelAnswer = ModelAnswer(text=most_common_genre[0][0],
                                            score=most_common_genre[0][1]/len(labels))
        return [answer]
    # @validate_video_loaded
    # @Agent.to_fallback(Operation.EXTRACT_GENRE, ComponentType.MODEL)
    # def extract_genre(self) -> ModelAnswer:
        
    #     model = self.components[0]
    #     model.set_video(self.video_frames)
    #     return model.execute()
    
    @validate_video_loaded
    @Agent.to_fallback(Operation.EXTRACT_VIDEO_FEATURES, ComponentType.MODEL)
    def get_game_features(self, questions: List[TextQuestion]) -> List[ModelAnswer]:
               
        videoQuestion = VideoQuestion(video_frames=self.video_frames, text="detect")
        videoQuestion.metadata["content"] = list((question.text, question.metadata["feature_type"]) for question in questions)
        videoQuestion.metadata["num_frames_to_read"] = VLMGaming.num_frames_to_read
        videoQuestion.metadata["clip_duration_seconds"] = VLMGaming.clip_duration_seconds
        videoAnswers = super().component_intersect_results_fn(videoQuestion, ModelClient.run_model)
                
        answers: List[ModelAnswer] = list()
        for videoAnswer in videoAnswers:
            for classified_label in videoAnswer.classified_labels:
                answer: ModelAnswer = ModelAnswer(text=classified_label.feature_type,
                                                  score=classified_label.score,
                                                  metadata={
                                                    "keyword": classified_label.label,
                                                    "video_frame": videoAnswer.text
                                                })
                answers.append(answer)
        return answers

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
