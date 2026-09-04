import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.agents.entities.component import Answer
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

    def execute(self, question: Question, max_results) -> List[Answer]:
        return super().execute(question, self.extract, max_results)
    
    # Make predictions
    def extract(self, question: TextQuestion, max_results) -> List[Answer]:
                
        results = self.model(question.text)
        
        answers: List[Answer] = list()
        for result in results:
            if float(result["score"]) > float(self.config["confidence_threshold"]):
                textAnswer = TextAnswer(text=result["word"].lower().strip(), score=float(result["score"]))
                answers.append(textAnswer)
        
        return answers
        
