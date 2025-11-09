import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from innovation.FeedbackerAi.agents.entities.question import Question
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from typing import Optional, Dict, Any, List, Set

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

    def execute(self, question: Question) -> Set[Answer]:
        return super().execute(question, self.extract)
    
    # Make predictions
    def extract(self, question: TextQuestion) -> Set[Answer]:
                
        results = self.model(question.text)
        
        answers: Set[Answer] = []
        for result in results:
            if float(result["score"]) > float(self.config["confidence_threshold"]):
                answers.update(TextAnswer(text=result["word"].lower().strip(), score=result["score"]))
        
        return answers
        
