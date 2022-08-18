class User:
    def __init__(self, json):
        assert isinstance(json, dict)
        self.json = json
        self.id = json['id']
        self.email = json['email']
        self.udid = None


class Users:
    def __init__(self, json):
        assert isinstance(json, list)
        self.__json = json

        self.__by_email = {}
        self.__by_id = {}

        for item in json:
            user = User(item)
            self.__by_email[user.email] = user
            self.__by_id[user.id] = user.email

    def by_email(self, email):
        return self.__by_email[email]

    def by_id(self, id):
        return self.by_email(self.__by_id[id])

    def emails(self):
        return self.__by_email.keys()
