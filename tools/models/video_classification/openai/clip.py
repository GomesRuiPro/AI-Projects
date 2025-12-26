import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, AutoConfig, pipeline
from innovation.FeedbackerAi.tools.models.model import VideoFeatureModel
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.local.utilities import Utility

from innovation.FeedbackerAi.tools.models.entities.video import VideoAnswer, ClassifiedLabel
from innovation.FeedbackerAi.tools.models.entities.video import VideoQuestion
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE

class Clip(VideoFeatureModel):
    
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    model_transform_params = {
        "openai/clip-vit-base-patch32": {
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
            self.model = pipeline('zero-shot-image-classification', model=self.model_name)
            
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

    # def set_device(self, video_frame, video_metadata=None):
    #     # Test which device to use
    #     self.model.eval()
    # 
    #     if video_metadata is not None:
    #         try:
    #             self.classify(video_frame, video_metadata)
    #         except NotImplementedError as error:
    #             if self.device == 'cpu':
    #                 raise error
    #             print(
    #                 f"Warning: Operation is not available for {self.device}. Attempting with cpu...")
    #             self.model = self.model.to('cpu')
    #             self.set_device(video_frame, video_metadata)
                
    def execute(self, video_question: Question, max_results) -> List[Answer]:
        return super().execute(video_question, self.classify, max_results)
    
    # Make predictions
    def classify(self, video_frame, video_metadata_content: List[tuple], max_results) -> List[Answer]:
        
        video_frame_transformed = self.transform(video_frame)
        
        video_labels = [content[0] for content in video_metadata_content]
        results = self.model(video_frame_transformed, candidate_labels=video_labels)
        
        classified_labels: List[ClassifiedLabel] = list()
        for result in results:
            if float(result["score"]) > float(self.config["confidence_threshold"]):
                classified_labels.append(ClassifiedLabel(label=result["label"],
                                                         debug_box=None,
                                                         score=float(result["score"]),
                                                         feature_type=next(obj[1] for obj in video_metadata_content if obj[0] == result["label"])))
            
        if classified_labels:    
            return [VideoAnswer(text="", score=0.0, classified_labels=classified_labels)]
            
        return []
        
    # def inference(self, video_frame, max_results) -> List[Answer]:
    #     video_frame_transformed = self.transform(video_frame)
        
    #     # Prepare inputs for CLIP
    #     inputs = self.processor(text=self.class_names, images=video_frame_transformed, return_tensors="pt", padding=True)
    #     # Move all input tensors to the correct device
    #     inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
    #     answers: List[Answer] = []
    #     with torch.no_grad():
    #         # Get text and image embeddings
    #         text_features = self.model.get_text_features(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
    #         image_features = self.model.get_image_features(pixel_values=inputs['pixel_values'])
            
    #         # Normalize features
    #         text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    #         image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
    #         # Compute similarities
    #         similarities = []
    #         for text_feature in text_features:
    #             similarity = torch.cosine_similarity(image_features, text_feature, dim=1)
    #             similarities.append(similarity.item())

    #         # Find all classes with similarity above the threshold
    #         matching_classes = [ClassifiedLabel(self.class_names[i], score) for i, score in enumerate(similarities) if score >= float(self.config["confidence_threshold"])]
    #         answers.update(VideoAnswer(matching_classes))
    #     if text_features.numel() == 0 and image_features.numel() == 0:
    #         return None
        
    #     return matching_classes, None # classes detected, detection boxes
    
    # def get_predictions(self, video_frame, matching_classes):
    #     predicted = {}
            
    #     Utility.log("Class labels:")
    #     for matching_class in matching_classes:
    #         label, score = matching_class
    #         Utility.log(f"{label}: {score}")
            
    #         predicted[total] 
    #         predicted[label] = score
                
    #     return {k: (lambda v: v / video_frame)(v)
    #         for k, v in predicted.items()}
    
    # def inference(self, video_frame):        
    #     # Generate candidate regions (for simplicity, a grid)

    #     detections = []

    #     # for y in range(0, frame_height - region_size + 1, step_size):
    #     #     for x in range(0, frame_width - region_size + 1, step_size):
    #     region_transformed = self.transform(video_frame)
    #     frame_height, frame_width = region_transformed.shape[:2]
    #     for y in range(0, frame_height + 1):
    #         for x in range(0, frame_width + 1):
    #             # Crop region
    #             # region = video_frame[y:y+region_size, x:x+region_size]
    #             # Transform and prepare input for CLIP
    #             inputs = self.processor(text=self.class_names, images=region_transformed.unsqueeze(0), return_tensors="pt", padding=True)
    #             inputs = {k: v.to(self.device) for k, v in inputs.items()}

    #             with torch.no_grad():
    #                 text_features = self.model.get_text_features(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
    #                 image_features = self.model.get_image_features(pixel_values=inputs['pixel_values'])
                    
    #                 # Normalize features
    #                 text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    #                 image_features = image_features / image_features.norm(dim=-1, keepdim=True)

    #                 # Compute similarity with text features
    #                 similarity = (image_features @ text_features.T).squeeze(0)  # shape: (num_classes,)
    #                 max_score, max_idx = similarity.max(0)

    #                 # Check if max score exceeds threshold
    #                 if max_score.item() > float(self.config["confidence_threshold"]):
    #                     detected_class = self.class_names[max_idx]
    #                     detections.append({
    #                         'boxes': (x, y, frame_width, frame_height),
    #                         'scores': max_score.item(),
    #                         'labels': detected_class
    #                     })
    #     return detections
