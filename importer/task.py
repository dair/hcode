import datetime


class Task:
    def __init__(self, json):
        assert isinstance(json, dict)
        self.json = json
        self.subtasks = []
        self.comments = []
        self.udid = None

    def result_data(self):
        body = self.json["body"]
        if len(self.comments) > 0:
            body = body + "\n\nКомментарии:\n\n"
            for comment in self.comments:
                body += comment.json["created_by_email"] + ", " + \
                        datetime.datetime.fromtimestamp(comment.json["updated_on"]).strftime('%c') + "\n"
                body += comment.json[body] + "\n\n"

        return {
            "title": self.json["name"],
            "description": body,
            "archived": self.json["is_trashed"],
            "completed": (self.json["completed_on"] is not None),
            "assigned": [self.json["assignee_id"]],
        }