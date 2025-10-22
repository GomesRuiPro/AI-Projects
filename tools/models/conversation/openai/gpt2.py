import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class Gpt2(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('text-generation', model=self.model_name)

    def execute(self, question):
        super().execute(question, self.generate_text)
    
    # Make predictions
    def generate_text(self, question):
        answers = self.model(question, max_new_tokens=30, truncation=True, num_return_sequences=5)
        if self.to_debug:
            print(f"Provided answers: {answers}")
        return answers[0]['generated_text'] # Chooses the first
        
