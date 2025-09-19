from abc import ABC, abstractmethod
class Model(ABC):

    model = None
    name = None
    pretrained = None
    version = None
    is_local = None

    def __init__(self, name, version, pretrained, is_local):
        self.name = name
        self.pretrained = pretrained
        self.version = version
        self.is_local = is_local

    @abstractmethod
    def execute(self, video_path):
        pass    