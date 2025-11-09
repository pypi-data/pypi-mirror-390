class PromptTemplate:
    def __init__(self, template: str, variables: dict):
        self.template = template
        self.variables = variables

    def render(self, **kwargs):
        # 合并固定变量和动态变量
        all_vars = {**self.variables, **kwargs}
        return self.template.format(**all_vars)
