# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
import json
import csv
import zipfile
from users import Users
from project_tasks import ProjectTasks
from project import Project
from yougile_api import Yougile
from task import Task
from comment import Comment


def parse_users(filename):
    with open(filename) as f:
        json_data = json.load(f)
        users = Users(json_data)
        return users


def parse_project_tasks(inzip_file):
    json_data = json.load(inzip_file)
    tasks = []
    for item in json_data:
        tasks.append(Task(item))
    return tasks


def parse_project_comments(inzip_file):
    json_data = json.load(inzip_file)
    comments = []
    for item in json_data:
        if item["parent_type"] == "Task":
            comments.append(Comment(item))
    return comments


def parse_project_obj(inzip_file):
    json_data = json.load(inzip_file)
    return Project(json_data)


def parse_project(filename):
    assert zipfile.is_zipfile(filename)

    with zipfile.ZipFile(filename, 'r') as file:
        project = None
        tasks = None
        subtasks = None
        comments = None

        for inzip_dir_filename in file.namelist():
            inzip_filename = os.path.split(inzip_dir_filename)[1]
            if inzip_filename == "tasks.json":
                with file.open(inzip_dir_filename, 'r') as inzip_file:
                    tasks = parse_project_tasks(inzip_file)
            elif inzip_filename == "project.json":
                with file.open(inzip_dir_filename, 'r') as inzip_file:
                    project = parse_project_obj(inzip_file)
            elif inzip_filename == "subtasks.json":
                with file.open(inzip_dir_filename, 'r') as inzip_file:
                    subtasks = parse_project_tasks(inzip_file)
            elif inzip_filename == "comments.json":
                with file.open(inzip_dir_filename, 'r') as inzip_file:
                    comments = parse_project_comments(inzip_file)
            else:
                print(inzip_filename)

        tasks_by_id = {}
        if tasks is not None and len(tasks) > 0:
            for task in tasks:
                tasks_by_id[task.json["id"]] = task

        if subtasks is not None and len(subtasks) > 0:
            for subtask in subtasks:
                task_id = subtask.json["task_id"]
                if task_id in tasks_by_id:
                    tasks_by_id[task_id].subtasks.append(subtask)
                    tasks_by_id[subtask.json["id"]] = subtask

        if comments is not None and len(comments) > 0:
            for comment in comments:
                parent_id = comment.json["parent_id"]
                if parent_id in tasks_by_id:
                    tasks_by_id[parent_id].comments.append(comment)

        if project is not None and tasks is not None:
            project.set_tasks(tasks)
        return project



def main():
    assert len(sys.argv) >= 2
    source_directory = sys.argv[1]
    bearer = sys.argv[2]

    sender = Yougile(bearer)

    users_filename = os.path.join(source_directory, "users.json")

    users = parse_users(users_filename)

    existing_users = sender.get_existing_users()
    for existing_user in existing_users:
        user = users.by_email(existing_user)
        if user:
            user.udid = existing_users[existing_user]

    for email in users.emails():
        user = users.by_email(email)
        if user.udid is None:
            result = sender.post("https://yougile.com/api-v2/users", {"email": user.email, "isAdmin": False})
            new_id = result["id"]
            user.udid = new_id



    projects_directory = os.path.join(source_directory, "projects")

    project_files = os.listdir(projects_directory)
    for file in project_files:
        project_file = os.path.join(projects_directory, file)
        project = parse_project(project_file)

        # собрать всех юзеров проекта
        all_user_ids = set()
        for task in project.tasks:
            all_user_ids.add(task.json["assignee_id"])
            all_user_ids.add(task.json["created_by_id"])
            all_user_ids.add(task.json["completed_by_id"])

        all_user_udids = {}
        for id in all_user_ids:
            user = users.by_id(id)
            if user is not None and user.udid is not None:
                all_user_udids[user.udid] = "worker"
            else:
                print("User " + str(id) + ": no user or udid")

        project_data = {"title": project.json["name"], "users": all_user_udids}
        result = sender.post("https://yougile.com/api-v2/projects", project_data)
        project_udid = result["id"]
        project.udid = project_udid

        board_data = {"title": "Доска", "projectId": project.udid}
        result = sender.post("https://yougile.com/api-v2/boards", board_data)
        board_id = result["id"]

        column_data = {"title": "Задачи", "color": 14, "boardId": board_id}
        result = sender.post("https://yougile.com/api-v2/columns", column_data)
        column_id = result["id"]

        for task in project.tasks:
            for subtask in task.subtasks:
                data = subtask.result_data()
                user_id = subtask.json["assignee_id"]
                user = users.by_id(user_id)
                if user is not None and user.udid is not None:
                    user_udid = user.udid
                    if user_udid == 0:
                        print("WAT")
                    data["assigned"] = [user_udid]
                data["columnId"] = column_id

                result = sender.post("https://yougile.com/api-v2/tasks", data)
                subtask.udid = result["id"]

            data = task.result_data()
            if "assignee_id" in task.json:
                user_id = task.json["assignee_id"]
                user = users.by_id(user_id)
                if user is not None and user.udid is not None:
                    user_udid = user.udid
                    if user_udid == 0:
                        print("WAT")
                    data["assigned"] = [user_udid]
                else:
                    print("User " + str(user_id) + ": no user or udid")

            data["columnId"] = column_id

            result = sender.post("https://yougile.com/api-v2/tasks", data)
            task.udid = result["id"]

if __name__ == '__main__':
    main()
