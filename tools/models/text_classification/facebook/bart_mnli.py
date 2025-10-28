import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class BartMnli(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline("zero-shot-classification", model=self.model_name)

    def execute(self, question):
        return super().execute(question, self.classify)
    
    # Make predictions
    def classify(self, question: tuple):
        context, labels = question
        answers = self.model(context, labels)
        
        results = []
        for answer in answers:
            if float(answer["scores"][0]) > float(self.config["confidence_threshold"]):
                result: tuple = (answer["sequence"], answer["labels"][0].lower(), answer["scores"][0])
                results.append(result)
        
        return set(results)
        
