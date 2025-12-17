from innovation.FeedbackerAi.tools.local.entities.component import Component


class DoNothing(Component):
    def __init__(self):
        super().__init__(None, None)

    def execute(self):
        return None
