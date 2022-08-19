class User:
    def __init__(self, json):
        assert isinstance(json, dict)
        self.json = json
        self.id = json['id']
        email = json['email']
        actual_email = email.replace("@", "-") + "@dair.spb.ru"
        self.email = actual_email
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
            self.__by_id[user.id] = user

    def by_email(self, email):
        if email in self.__by_email:
            return self.__by_email[email]
        else:
            return None

    def by_id(self, id):
        if id in self.__by_id:
            return self.__by_id[id]
        else:
            return None

    def emails(self):
        return self.__by_email.keys()
