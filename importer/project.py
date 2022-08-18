class Project:
    def __init__(self, json):
        assert isinstance(json, dict)
        self.json = json
        self.tasks = []
        self.udid = None

    def set_tasks(self, tasks):
        self.tasks = tasks

