import torch.hub as hub
from innovation.FeedbackerAi.tools.models.model import VideoModel
from typing import Optional, Dict, Any


class PytorchVideo(VideoModel):

    mean = [0.45, 0.45, 0.45]
    std = [0.225, 0.225, 0.225]
    frames_per_second = 30
    model_transform_params = {
        "x3d_xs": {
            "side_size": 182,
            "crop_size": 182,
            "num_frames": 4,
            "sampling_rate": 12,
        },
        "x3d_s": {
            "side_size": 182,
            "crop_size": 182,
            "num_frames": 13,
            "sampling_rate": 6,
        },
        "x3d_m": {
            "side_size": 256,
            "crop_size": 256,
            "num_frames": 16,
            "sampling_rate": 5,
        }
    }

    def __init__(self, config, device, pretrained, num_frames):
        super().__init__(config, device, pretrained, num_frames)

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None  # TBD
        else:
            root_repository = "facebookresearch/pytorchvideo"
            repository_name = root_repository
            # Make sure the model is available in pytorch repository
            self.model = hub.load(repository_name, self.name+"_" +
                                  self.version, pretrained=self.pretrained)

        # Prepare model
        self.model = self.model.eval()
        self.model = self.model.to(self.device)

        # Get transform parameters based on model
        transform_params = self.model_transform_params[self.name+"_"+self.version]

        # Note that this transform is specific to the slow_R50 model.
        # self.transform =  Compose(
        #     [
        #         UniformTemporalSubsample(transform_params["num_frames"]),
        #         Lambda(lambda x: x/255.0),
        #         NormalizeVideo(self.mean, self.std),
        #         ShortSideScale(size=transform_params["side_size"]),
        #         CenterCropVideo(
        #             crop_size=(transform_params["crop_size"], transform_params["crop_size"])
        #         )
        #     ]
        # )

        self.num_frames = transform_params["num_frames"]

        # The duration of the input clip is also specific to the model.
        self.clip_duration = (
            transform_params["num_frames"] * transform_params["sampling_rate"])/self.frames_per_second

        # Preprocessing transforms (resize, normalize)
        # frames_resolution = self.config["frames_resolution"].split("x")
        # self.transform = transforms.Compose([
        #     transforms.ToPILImage(),
        #     transforms.Resize((int(frames_resolution[1]), int(frames_resolution[0]))),
        #     transforms.ToTensor(),
        #     transforms.Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
        # ])

    def execute(self, video_frames):

        # Setup model
        if not self.model:
            self.setup()

        # Preprocess frames
        video_tensor = super().prepare_video(video_frames)

        # Move the inputs to the desired device
        video_tensor = video_tensor.to(self.device)

        # Set to evaluation mode
        self.model.eval()

        # Perform inference
        try:
            predicted = super()._run_model(video_tensor, self.model)
        except NotImplementedError as error:
            print(
                f"Warning: Operation is not available for {self.device}. Attempting with cpu...")
            video_tensor = video_tensor.to('cpu')
            model = self.model.to('cpu')
            predicted = super()._run_model(video_tensor, model)

        # Print the result
        confidence, predicted_class = predicted
        print(f'Predicted class index: {predicted_class.item()}')
        print(f'Confidence: {confidence.item():.4f}')
