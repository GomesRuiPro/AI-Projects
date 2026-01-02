import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, AutoConfig, pipeline
from innovation.FeedbackerAi.tools.models.model import VideoModel
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.local.utilities import Utility

from innovation.FeedbackerAi.tools.models.entities.video import VideoAnswer, ClassifiedLabel
from innovation.FeedbackerAi.tools.models.entities.video import VideoQuestion
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE

class BartMnli(VideoModel):
    
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    model_transform_params = {
        "facebook/bart-large-mnli": {
            "side_size": 256,  # To force replace the default resolution from config - specific to model
            "crop_size": 224,  # To force replace the default resolution from config - specific to model
            # "max_num_frames": 4, # To force replacing the default max_num_frames from config - specific to model
            # "sampling_rate": 12, # To force replace the default clip duration from config - specific to model
            # "frames_per_second": 30, # To force replace the default clip duration from config - specific to model
        }
    }

    def __init__(self, config, token, model_name, device, pretrained, to_debug):
        super().__init__(config, model_name, device, pretrained, to_debug)
        self.token = token
        
    def setup(self):

        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('zero-shot-classification', model=self.model_name)
            
        # # Prepare model
        # self.model = self.model.to(self.device)

        # Get transform parameters based on model
        transform_params = self.model_transform_params[
            self.model_name] if self.model_name in self.model_transform_params else None

        # Note that this transform is specific to the slow_R50 model.
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize(transform_params['side_size']),
                transforms.CenterCrop(transform_params['crop_size']),
                # transforms.ToTensor(),
                # transforms.Normalize(self.mean, self.std),
            ]
        )

        if "max_num_frames" in transform_params or self.num_frames_to_read is None:
            self.num_frames_to_read = transform_params["max_num_frames"]

        # The duration of the input clip is also specific to the model.
        if ("sampling_rate" in transform_params and "frames_per_second" in transform_params) or self.clip_duration_seconds is None:
            self.clip_duration_seconds = int(round(
                (self.num_frames_to_read * transform_params["sampling_rate"])/transform_params["frames_per_second"]))
                
    def execute(self, video_question: Question, max_results) -> List[Answer]:
        return super().execute(video_question, self.classify, max_results)
    
    # Make predictions
    def classify(self, video_frame, video_metadata_content: List[str], max_results) -> List[Answer]:
        
        video_frame_transformed = self.transform(video_frame)
        
        results = self.model(video_frame_transformed, candidate_labels=video_metadata_content)
        
        videoAnswer = None
        for result in results:
            if float(result["score"]) > float(self.config["confidence_threshold"]) and float(result["score"]) > videoAnswer.score:
                videoAnswer = VideoAnswer(text=result["label"], score=result["score"])
            
        return [videoAnswer]
      