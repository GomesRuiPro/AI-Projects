from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any
import torch
import os


class Model(ABC):
    
    model = None

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
    
    def execute(self, question, model_execute_fn=None):
         # Setup model
        if not self.model:
            self.setup()

            # Get predictions
            if model_execute_fn:
                results = model_execute_fn(question)
            
            if results is None:
                if self.to_debug:
                    print(f"No answer found for question: {question}")
                return None
            
            if self.to_debug:
                print(f"Answers found for the question asked: {results}")

        return results
    
class VideoModel(Model, ABC):  # Used for get Genre where we do not expect to extract features

    def __init__(self, config, model_name, device, pretrained, to_debug):
        super().__init__(config, model_name)
        self.pretrained = pretrained
        self.video_frames = None
        self.to_debug = to_debug
        if 'cuda' in device:
            self.device = torch.device(
                'cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        # Set CUDA_LAUNCH_BLOCKING to '1' for debugging
        os.environ['CUDA_LAUNCH_BLOCKING'] = str(device)

    def set_video(self, video_frames):
        self.video_frames = video_frames

    @abstractmethod
    def setup(self, num_frames_to_read=None, clip_duration_seconds=None, video_frame=None):
        pass


# Used for run computer vision models where we do expect to extract features
class VideoFeatureModel(VideoModel, ABC):
    def __init__(self, config, model_name, device, pretrained, to_debug):
        super().__init__(config, model_name, device, pretrained, to_debug)

    # def tensory(self):

    #     start_sec = 0
    #     end_sec = start_sec + self.clip_duration_seconds

    #     # using 3 channel RGB frame
    #     frames = [self.transform(frame[:3, :, :])
    #               for frame in self.video_frames]
    #     video_tensor = torch.stack(frames)
    #     video_tensor = video_tensor.permute(1, 0, 2, 3)
    #     video_tensor = video_tensor.unsqueeze(0)  # shape: (1, C, T, H, W)

    #     # # Apply padding
    #     # total_frames = len(frames)
    #     # if total_frames >= self.max_num_frames:
    #     #     start = torch.randint(0, total_frames - self.max_num_frames + 1, (1,)).item()
    #     #     video_tensor = video_tensor[start:start + self.max_num_frames]
    #     # else:
    #     #     # Pad if too short
    #     #     pad_len = self.max_num_frames - total_frames
    #     #     pad_shape = (pad_len, *video_tensor.shape[1:])
    #     #     pad = torch.zeros(pad_shape, dtype=video_tensor.dtype)
    #     #     video_tensor = torch.cat([video_tensor, pad], dim=0)

    #     return video_tensor

    # def execute(self, video_tensor, model):

    #     with torch.no_grad():
    #         outputs = model(video_tensor)
    #         probs = torch.nn.functional.softmax(outputs, dim=1)
    #         return torch.max(probs, dim=1)

    def execute(self, num_frames_to_read, clip_duration_seconds, model_execute_fn=None):
        # Setup model
        if not self.model:
            self.setup(num_frames_to_read, clip_duration_seconds,
                       self.video_frames[0])

        # Set to evaluation mode
        self.model.eval()

        predicted = {}
        eval_xtimes = int(round(num_frames_to_read / clip_duration_seconds))
        for index, video_frame in enumerate(self.video_frames):

            if (index + 1) % eval_xtimes != 0:
                continue

            # Get predictions
            if model_execute_fn:
                class_names, results = model_execute_fn(video_frame)
            
            if results is None:
                if self.to_debug:
                    print(f"No results founds in video_frame {index}")
                continue
            
            if class_names is None:
                raise Exception("No 'id2label' attribute found in the config.")
            
            if self.to_debug:
                print("Class labels:")
                for idx, label in class_names.items():
                    print(f"{idx}: {label}")
                
            if self.to_debug:
                Utility.show_image(video_frame, results, class_names)

            for class_name in class_names:
                if class_name not in predicted:
                    predicted[class_name] = 1
                else:
                    predicted[class_name] += 1

        predicted = {k: (lambda v: v / self.video_frames)(v)
                     for k, v in predicted.items()}
        return predicted
