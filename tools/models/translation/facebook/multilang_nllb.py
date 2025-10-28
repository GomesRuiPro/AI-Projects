import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class Multilang_Nllb(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('translation', model=self.model_name)

    def execute(self, question):
        return super().execute(question, self.translate)
    
    # Make predictions
    def translate(self, question):
        answer = self.model(question, tgt_lang="eng")
        return answer[0]['translation_text']
        
