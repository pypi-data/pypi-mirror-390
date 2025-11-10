# Import the library
import asana
import os
# Note: Replace this value with your own personal access token


# Construct an Asana client
client = asana.Client.access_token(os.environ["ASANA_TOKEN"])
client.headers['asana-enable'] = 'new_goal_memberships'
# Set things up to send the name of this script to us to show that you succeeded! This is optional.

# Get your user info
def get_tasks():
    me=client.users.me()
    tasks = []
    for i in me["workspaces"]:
        projects_ids = client.projects.get_projects_for_workspace(i["gid"])
        for j in projects_ids:
            task_list = list(client.tasks.get_tasks_for_project(j["gid"], opt_fields=["resource_type"
                , "name"
                , "completed"
                , "assignee.name"
                , "parent"
                , "created_at"
                , "permalink_url"
                , "memberships.section.name"
                                                                                      ]))
            task_list = [k | {"workspace": i["name"]} | {"project": j["name"]} for k in task_list]
            tasks.append(task_list)
    tasks=sum(tasks, [])
    return tasks

