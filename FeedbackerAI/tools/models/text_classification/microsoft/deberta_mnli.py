import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline, DebertaV2Tokenizer
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any, Set, List
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question

class DebertaMnli(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline("zero-shot-classification",
                                  model=self.model_name,
                                  tokenizer=DebertaV2Tokenizer.from_pretrained(self.model_name, use_fast=False))

    def execute(self, question: Question, max_results) -> List[Answer]:
        return super().execute(question, self.classify, max_results)
    
    # Make predictions
    def classify(self, question: TextQuestion, max_results) -> List[Answer]:
        context = question.text
        labels = question.metadata["labels"]
        # {'sequence': 'game', 'labels': ['technical', 'ui', 'monetization', 'sound', 'gameplay', 'social', 'story', 'graphics'], 'scores': [0.12559685111045837, 0.12559300661087036, 0.1253976821899414, 0.1250213235616684, 0.12499650567770004, 0.12479450553655624, 0.12471074610948563, 0.1238894984126091]}
        result = self.model(context, labels)
        
        answers: List[Answer] = list()
        if float(result["scores"][0]) > float(self.config["confidence_threshold"]):
            answers.append(TextAnswer(text=result["sequence"],
                                    score=float(result["scores"][0]),
                                    metadata={"labels": result["labels"][0].lower()}))
        return answers
        
