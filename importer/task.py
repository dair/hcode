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
            body = body + "<br>\n<br>\n<b>Комментарии:</b><br>\n<br>\n"
            self.comments.sort(key=lambda x: x.json["created_on"])
            for comment in self.comments:
                body += "<b>" + comment.json["created_by_name"] + " <" + comment.json["created_by_email"] + "></b>, <b>" + \
                        datetime.datetime.fromtimestamp(comment.json["created_on"]).strftime('%c') + "</b><br>\n"
                body += comment.json["body"] + "<br>\n<br>\n"

        title = "<Без заголовка>"
        if "name" in self.json:
            title = self.json["name"]

        return {
            "title": title,
            "description": body,
            "archived": self.json["is_trashed"],
            "completed": (self.json["completed_on"] is not None),
        }