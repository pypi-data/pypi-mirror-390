from todoist_api_python.api import TodoistAPI

def get_todoist_api(api_key: str) -> TodoistAPI:
    api = TodoistAPI(api_key)
    return api
