class ProjectTasks:
    def __init__(self, json):
        assert isinstance(json, list)
        self.__items = json
