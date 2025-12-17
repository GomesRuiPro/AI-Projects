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
import numpy as np

class AllMiniLML6V2(TextModel):

    def __init__(self, config, token, model_name, pretrained, to_debug):
        super().__init__(config, model_name, pretrained, to_debug)
        self.token = token

    def setup(self):
        # Init
        if self.config['is_local']:
            self.model = None
            pass
        else:  # calling hugging face
            self.model = pipeline('feature-extraction', model=self.model_name)

    def execute(self, question: Question, max_results) -> List[Answer]:
        return super().execute(question, self.classify, max_results)
    
    def __get_embedded(self, word):
        outputs = self.model(word)
        arr = np.array(outputs[0], dtype=float)
        return np.mean(arr, axis=0)
        
    # Make predictions
    def classify(self, question: TextQuestion, max_results) -> List[Answer]:    
        
        result_embedded = self.__get_embedded(question.text)
        answers: List[Answer] = list()
        labels = question.metadata["labels"]
        for label in labels:
            label_embedded = self.__get_embedded(label)
            similar_score = float(np.dot(result_embedded, label_embedded) / (np.linalg.norm(result_embedded) * np.linalg.norm(label_embedded)))
            
            if similar_score > float(self.config["confidence_threshold"]):
                textAnswer = TextAnswer(text=label, score=similar_score, metadata={"keyword": question.text})
                answers.append(textAnswer)
                
            if max_results:
                if len(answers) == max_results:
                    break
        
        return answers
        
