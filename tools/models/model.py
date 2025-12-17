from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from innovation.FeedbackerAi.tools.models.entities.video import VideoAnswer
from innovation.FeedbackerAi.tools.models.entities.video import VideoQuestion
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any, List, Set
import torch
import os


class Model(ABC):
    
    model = None
    component_type = ComponentType.MODEL

    def __init__(self, config, model_name):  # Used for fallback models
        self.model_name = model_name
        self.config = config
        
class TextModel(Model, ABC): # Used for text models
    def __init__(self, config, model_name, pretrained, to_debug):
        super().__init__(config, model_name)
        self.pretrained = pretrained
        self.to_debug = to_debug

    @abstractmethod
    def setup(self):
        pass
    
    def execute(self, question: TextQuestion, model_execute_fn=None, max_results=None) -> List[Answer]:
        
         # Setup model
        if not self.model:
            self.setup()

        # Get predictions
        if model_execute_fn:
            textAnswers = model_execute_fn(question, max_results)
        
        if not textAnswers:
            Utility.log(f"No answer found for question: {question.text}")
            return None
        
        Utility.log(f"Answers found for the question asked: {textAnswers}")
        return textAnswers
    
class VideoModel(Model, ABC):  # Used for get Genre where we do not expect to extract features

    def __init__(self, config, model_name, device, pretrained, to_debug):
        super().__init__(config, model_name)
        self.pretrained = pretrained
        self.num_frames_to_read = None
        self.clip_duration_seconds = None
        self.to_debug = to_debug
        if 'cuda' in device:
            self.device = torch.device(
                'cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        # Set CUDA_LAUNCH_BLOCKING to '1' for debugging
        os.environ['CUDA_LAUNCH_BLOCKING'] = str(device)

    @abstractmethod
    def setup(self, video_frames):
        pass


# Used for run computer vision models where we do expect to extract features
class VideoFeatureModel(VideoModel, ABC):
    def __init__(self, config, model_name, device, pretrained, to_debug):
        super().__init__(config, model_name, device, pretrained, to_debug)

    def execute(self, question: VideoQuestion, model_execute_fn=None, max_results=None) -> List[Answer]:
        
        video_frames = question.video_frames
        
        # Setup model
        if not self.model:
            self.setup(video_frames[0])

        # Set to evaluation mode
        self.model.eval()

        # predicted = {}
        # eval_xtimes = int(round(self.num_frames_to_read / self.clip_duration_seconds))
        key_pressed = None
        for index, video_frame in enumerate(video_frames):

            # if (index + 1) % eval_xtimes != 0:
            #     continue

            # Get predictions
            if model_execute_fn:
                videoAnswers = model_execute_fn(video_frame, max_results)
            
            if videoAnswers is None:
                Utility.log(f"No results founds in video_frame {index}")
                continue
            
            Utility.log(f"Results found in video_frame {index}")
            
            if self.to_debug and videoAnswers.debug_boxes and not (key_pressed == ord('q')):
                key_pressed = Utility.show_image(video_frame, videoAnswers)

        return videoAnswers
