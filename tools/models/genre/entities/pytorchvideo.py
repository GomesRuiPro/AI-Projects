import torch.hub as hub
import torch
from tools.models.genre.entities.model import Model

class PytorchVideo(Model):
        
    def __init__(self, model_name='x3d', model_version='xs', pretrained=True, is_local=False):
        super().__init__(model_name, model_version, pretrained, is_local)
        if is_local:
            self.model = None
        else:
            root_repository = "facebookresearch/pytorchvideo"
            repository_name = root_repository
            self.model = hub.load(repository_name, model_name+"_"+model_version, pretrained=pretrained)  # Make sure the model is available in pytorch repository

    def execute(self, video_path):
        # Set to evaluation mode
        self.model.eval()

        # Example input: a batch of videos with shape (batch_size, channels, time, height, width)
        # For example, a single video clip of 16 frames of size 112x112
        video = torch.randn(1, 3, 16, 112, 112)

        # Perform inference
        with torch.no_grad():
            output = self.model(video)
        return output
