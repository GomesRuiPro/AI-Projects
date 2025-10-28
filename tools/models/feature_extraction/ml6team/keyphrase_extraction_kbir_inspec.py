import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class KeyphraseExtractionKbirInspec(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('token-classification', model=self.model_name, aggregation_strategy="simple")

    def execute(self, question):
        return super().execute(question, self.extract)
    
    # Make predictions
    def extract(self, text):
        answers = self.model(text)
        
        results = []
        for answer in answers:
            if float(answer["score"]) > float(self.config["confidence_threshold"]):
                results.append(answer["word"].lower().strip())
        
        return set(results)
        
