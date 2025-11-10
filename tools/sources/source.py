from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer, SourceQuestion

class Source(ABC): # Used for fallback models
    
    def __init__(self):  
        pass
    
    def execute(self, question: SourceQuestion, source_execute_fn=None) -> Set[Answer]:

        # Get predictions
        if source_execute_fn:
            sourceAnswers = source_execute_fn(question)
        
        if not sourceAnswers:
            Utility.log(f"No answer found for question: {question.text}")
            return None
        
        Utility.log(f"Answers found for the question asked: {sourceAnswers if isinstance(sourceAnswers, str) else ','.join(sourceAnswers)}")
        return sourceAnswers

class Database(Source, ABC):

    def __init__(self):
        super().__init__()

class Webpage(Source, ABC):
    
    domain = None
    resource = None
    filter = ""
    
    def __init__(self, domain, resource, ui_component, filter=""):        
        super().__init__()
        self.domain = domain
        self.resource = resource
        self.filter = filter
        self.ui_component = ui_component
        
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.ui_component = Webpage.Component()
        
    def get_url(self):
        return f"https://{self.domain}{self.resource}{self.filter}"
    
    class Component(ABC):
        
        parent = None
        
        tags = {}

        def add(self, component) -> None:
            pass

        def remove(self, component) -> None:
            pass
        
        def stringify(self):
            return Utility.class_attrs_to_str(self)

        def is_composite(self):
            """
            You can provide a method that lets the client code figure out whether a
            component can bear children.
            """
            return False
            
    class Branch(Component):
        
        def __init__(self):
            self.child = None
            
        def __init__(self, _class=None, _id=None, _type=None, _name=None):
            self.tags = {
                "_id": _id,
                "_name": _name,
                "_class": _class,
                "_type": _type,
            }   
            self.child = None
        
        def add(self, component):
            self.child = component
            component.parent = self
            
        def remove(self):
            self.child = None
            
        def is_composite(self):
            return True                
        
    class Leaf(Component):
        
        def __init__(self, attr_to_fetch="value", type_to_fetch="div", _class=None, _id=None, _type=None, _name=None):
            self.attr_to_fetch = attr_to_fetch
            self.type_to_fetch = type_to_fetch
            self.tags = {
                "_id": _id,
                "_name": _name,
                "_class": _class,
                "_type": _type,
            }   
            
        def is_composite(self):
            return False     