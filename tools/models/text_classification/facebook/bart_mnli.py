import cv2
import torch
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from innovation.FeedbackerAi.tools.models.model import TextModel
from typing import Optional, Dict, Any, Set
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question

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

    def execute(self, question: Question) -> Set[Answer]:
        return super().execute(question, self.classify)
    
    # Make predictions
    def classify(self, question: TextQuestion) -> Set[Answer]:
        context = question.text
        labels = question.metadata["labels"]
        results = self.model(context, labels)
        
        answers: Set[Answer] = []
        for result in results:
            if float(result["scores"][0]) > float(self.config["confidence_threshold"]):
                answers.update(TextAnswer(text=result["sequence"],
                                      score=result["scores"][0],
                                      metadata={"labels": result["labels"][0].lower()}))
        return answers
        
