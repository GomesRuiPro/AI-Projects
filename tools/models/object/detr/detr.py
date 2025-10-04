import torch
from transformers import DetrForObjectDetection, DetrImageProcessor, AutoConfig
from torchvision import transforms
from tools.models.model import VideoFeatureModel
from PIL import Image


class Detr(VideoFeatureModel):
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    model_transform_params = {
        "facebook/detr-resnet-50": {
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
        self.processor = None

    def setup(self, num_frames_to_read=None, clip_duration_seconds=None, video_frame=None):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.processor = DetrImageProcessor.from_pretrained(
                self.model_name, token=self.token)
            self.model = DetrForObjectDetection.from_pretrained(
                self.model_name, token=self.token)
            self.model_config = AutoConfig.from_pretrained(
                self.model_name, token=self.token)

        # Prepare model
        self.model = self.model.to(self.device)

        # Get transform parameters based on model
        transform_params = self.model_transform_params[
            self.model_name] if self.model_name in self.model_transform_params else None

        # Note that this transform is specific to the slow_R50 model.
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize(transform_params['side_size']),
                transforms.CenterCrop(transform_params['crop_size'])
            ]
        )

        self.num_frames_to_read = num_frames_to_read
        if "max_num_frames" in transform_params or self.num_frames_to_read is None:
            self.num_frames_to_read = transform_params["max_num_frames"]

        # The duration of the input clip is also specific to the model.
        self.clip_duration_seconds = clip_duration_seconds
        if ("sampling_rate" in transform_params and "frames_per_second" in transform_params) or self.clip_duration_seconds is None:
            self.clip_duration_seconds = int(round(
                (self.num_frames_to_read * transform_params["sampling_rate"])/transform_params["frames_per_second"]))

        # Test which device to use
        if video_frame is not None:
            try:
                self.inference(video_frame)
            except NotImplementedError as error:
                print(
                    f"Warning: Operation is not available for {self.device}. Attempting with cpu...")
                self.model = self.model.to('cpu')

    def inference(self, video_frame):
        video_frame_transformed = self.transform(video_frame)
        inputs = self.processor(images=video_frame_transformed, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        return self.model(**inputs)

    def execute(self, num_frames_to_read, clip_duration_seconds):
        super().execute(num_frames_to_read, clip_duration_seconds, self.model_execution)

    def model_execution(self, video_frame):
        outputs = self.inference(video_frame)
        results = self.processor.post_process_object_detection(outputs, 
                                                            threshold=self.config['confidence_threshold'], 
                                                            target_sizes=[(video_frame.shape[1], video_frame.shape[2])])
        
        if len(results) > 1:
            raise Exception("Results length is higher than 1!")
        
        if hasattr(self.model_config, 'id2label'):
            return self.model_config.id2label, results[0]

        return None, results[0]
