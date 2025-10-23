import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class KeyphraseExtractionBert(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('feature-extraction', model=self.model_name, tokenizer=self.model_name)

    def execute(self, question):
        return super().execute(question, self.extract)
    
    # Make predictions
    def extract(self, text):
        answer = self.model(text)
        
        if float(answer["score"]) > float(self.config["confidence_threshold"]):
            return answer
        
        return None
        
