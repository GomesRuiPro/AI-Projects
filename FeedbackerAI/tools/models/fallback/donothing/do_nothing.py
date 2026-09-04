from tools.models.model import Model


class DoNothing(Model):
    def __init__(self):
        super().__init__(None, None)

    def execute(self):
        return None
