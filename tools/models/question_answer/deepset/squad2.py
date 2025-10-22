import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any

class Squad2(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('question-answering', model=self.model_name)

    def execute(self, question):
        super().execute(question, self.talk)
    
    # Make predictions
    def talk(self, question_context):
        question, context = question_context
        answer = self.model(question=question, context=context)
        return answer
        
