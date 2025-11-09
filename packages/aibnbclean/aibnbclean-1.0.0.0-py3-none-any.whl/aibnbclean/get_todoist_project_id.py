from todoist_api_python.api import TodoistAPI

def get_todoist_project_id(project_name: str, api: TodoistAPI) -> str:
    response = api.get_projects()
    for projects in response:
        for project in projects:
            if project.name == project_name:
                return project.id
    raise Exception(f"unable to find project id for {project_name}")
