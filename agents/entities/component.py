from dataclasses import dataclass, asdict, field
from inspect import ismethod
from typing import List
import json

@dataclass
class Answer:
    text: str = field(default=None)
    metadata: dict = field(default_factory=dict, compare=False)
    score: float = field(default=1.0, compare=False)
    
    # def __hash__(self):
    #     return hash(self.text)

    # def __eq__(self, other):
    #     if not isinstance(other, Answer):
    #         return None
    #     return self.text == other.text
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)
    
@dataclass
class Question:
    text: str = field(default=None)
    metadata: dict = field(default_factory=dict, compare=False)
    # method_fn: ismethod = field(default=None, compare=False)
    
    # def __hash__(self):
    #     return hash(self.text)

    # def __eq__(self, other):
    #     if not isinstance(other, Question):
    #         return None
    #     return self.text == other.text
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)
    
@dataclass
class ComponentData:
    answers: List[Answer] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
    __operation: object = field(default=None)
    
    def get_operation(self):
        return self.__operation
    
    def set_operation(self, operation):
        self.questions.clear()
        self.answers.clear()
        self.__operation = operation
        
    def get_last_answer(self):
        return self.answers[-1]
    def get_last_question(self):
        return self.questions[-1]
    def pop(self):
        answer = self.answers.pop()
        question = self.questions.pop()
        operation = self.operation
        self.operation = None
        return question, answer, operation
