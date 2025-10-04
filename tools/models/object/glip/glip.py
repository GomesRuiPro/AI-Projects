import torch
from transformers import DetrForObjectDetection, DetrImageProcessor
from torchvision import transforms
from tools.models.model import VideoFeatureModel
from PIL import Image


class Glip(VideoFeatureModel):
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    frames_per_second = 30
    frames_resolution = "800x600"
    model_transform_params = {
        "glip-grounded-detr": {
            "side_size": 182,
            "crop_size": 182,
            "num_frames": 4,
            "sampling_rate": 12,
        }
    }

    def __init__(self, config, token, model_name, device, pretrained, num_frames):
        super().__init__(config, model_name, device, pretrained, num_frames)
        self.token = token
        self.processor = None

    def setup(self, video_frame=None):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.processor = DetrImageProcessor.from_pretrained(
                self.model_name, token=self.token)
            self.model = DetrForObjectDetection.from_pretrained(
                self.model_name, token=self.token)

        # Prepare model
        self.model = self.model.to(self.device)

        # Get transform parameters based on model
        transform_params = self.model_transform_params[self.model_name]

        # Note that this transform is specific to the slow_R50 model.
        clip_resolution = self.config["frames_resolution"].split("x")
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((int(clip_resolution[1]), int(clip_resolution[0]))),
                transforms.ToTensor(),
                transforms.Normalize(self.mean, self.std),
            ]
        )

        self.num_frames = transform_params["num_frames"]

        # The duration of the input clip is also specific to the model.
        self.clip_duration = (
            transform_params["num_frames"] * transform_params["sampling_rate"])/self.frames_per_second

        if video_frame:
            try:
                self.inference(video_frame)
            except NotImplementedError as error:
                print(
                    f"Warning: Operation is not available for {self.device}. Attempting with cpu...")
                self.model = self.model.to('cpu')

    def inference(self, video_frame):
        inputs = self.processor(images=video_frame, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        return self.model(**inputs)

    def execute(self):

        # Setup model
        if not self.model_name:
            self.setup(self.video_frames[0])

        # Preprocess frames
        # video_tensor = super().tensory(video_frames)

        # Move the inputs to the desired device
        # video_tensor = video_tensor.to(self.device)

        # Set to evaluation mode
        self.model.eval()

        predicted = {}

        for video_frame in self.video_frames:
            outputs = self.inference(video_frame)

            # Get predictions
            logits = outputs.logits  # shape: [num_queries, num_classes]
            bboxes = outputs.bboxes  # shape: [num_queries, 4]

            # Filter predictions
            probs = logits.softmax(-1)
            max_probs, labels = probs.max(-1)

            # Filter based on threshold
            keep = max_probs > int(self.config['confidence_threshold'])

            boxes = bboxes[keep]
            labels = labels[keep]
            scores = max_probs[keep]

            # Map label indices to class names
            class_names = self.processor.model.config.id2label
            for class_name in class_names:
                if class_name not in predicted:
                    predicted[class_name] = 1
                else:
                    predicted[class_name] += 1

        predicted = {k: (lambda v: v / self.video_frames)(v)
                     for k, v in predicted.items()}
        return predicted
