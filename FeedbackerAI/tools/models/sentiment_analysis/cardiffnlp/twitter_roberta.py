import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any, Set, List

class TwitterRoberta(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('sentiment-analysis', model=self.model_name, tokenizer=self.model_name)

    def execute(self, question: Question, max_results) -> List[Answer]:
        return super().execute(question, self.analyse, max_results)
    
    # Make predictions
    def analyse(self, question: TextQuestion, max_results) -> List[Answer]:
        
        result = self.model(question.text,
                            max_length=self.config["max_length"],
                            padding='max_length',
                            truncation=True)[0]
        
        if float(result["score"]) > float(self.config["confidence_threshold"]):
            return [TextAnswer(text=result["label"].lower().strip(), score=float(result["score"]))]
        
        return []
        
