class StepFunction:
    def __init__(self, name, function, post_functions=None):

        self.function = function
        self.name = name
        self.post_functions = post_functions

    def run_func(self):
        return self.function()

    def run_post_func(self,context):
        if self.post_functions is not None:
            self.post_functions(context)