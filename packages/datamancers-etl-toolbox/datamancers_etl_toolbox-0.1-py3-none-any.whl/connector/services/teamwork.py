# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 00:55:08 2021

@author: vitmr
"""

import scripts.extract.teamwork as teamwork
import json
import pandas as pd
import requests

class instance():
    def __init__(self, workspace_domain, token):
        self.instance = teamwork.Teamwork(workspace_domain, token)
        self.user = self.instance._user.id


    def getProjects(self,activeProjects=[]):
        projects = self.instance.get_projects()
        pd_projects = pd.DataFrame([(i["id"], i["name"]) for i in projects], columns=["project_id", "project_name"])
        if activeProjects != []:
            pd_projects = pd_projects[pd_projects["project_name"].isin(activeProjects)]
        return pd_projects

    def getTimeEntries(self, start, end):
        params = {"start": start, "end": end}
        response_timeEntries = self.get_call(path="/user/" + self.getUserId() + "/time-entries", params=params)
        # pd_clients=pd.DataFrame([(i["id"],i["name"]) for i in response_clients],columns=["client_id","client_name"])
        return response_timeEntries

    def getTaskLists(self,projects_filter=[]):
        json_taskLists = self.instance.get(path="tasklists.json")
        df_taskLists = pd.json_normalize(json_taskLists["tasklists"])
        if projects_filter != []:
            df_taskLists = df_taskLists.loc[df_taskLists["projectId"].isin(projects_filter)]
        return df_taskLists



    def getTasks(self,projects_filter=[]):
        json_tasks = self.instance.get(path="tasks.json",params={"pageSize":200})
        df_tasks = pd.json_normalize(json_tasks["todo-items"])
        df_tasks = df_tasks.loc[df_tasks["completed"]==False]
        if projects_filter != []:
            df_tasks = df_tasks.loc[df_tasks["project-id"].isin(projects_filter)]
        return df_tasks

    def getAllWorkspaceElements(self):
        projects = self.getProjects()
        clients = self.getClients()
        tasks = self.getTasks()
        workspace_elements = clients.merge(projects.merge(tasks, on="project_id", how="left"), on="client_id",
                                           how="left")
        return workspace_elements

    def post_call(self, endpoint, json_input):
        try:
            request_call = requests.post(self.endpoint_basic + endpoint + "/", json=json_input, headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise Exception(e)

    def createProjects(self, projectSetup_list, client_id):
        unique_list = projectSetup_list[["client_name", "color"]].drop_duplicates(["client_name"])
        print(unique_list)
        for i in range(len(unique_list)):
            json_input = {"name": unique_list["client_name"].iloc[i].ljust(2, "_")
                , "clientId": client_id
                , "billable": "true"
                , "isPublic": "false"
                , "color": unique_list["color"].iloc[i]
                          }
            print(json_input)
            response_projects = self.post_call(endpoint="projects", json_input=json_input)

    def createTasks(self, taskSetup_list):
        unique_list = taskSetup_list[["project_id", "project_task", "task_estimate"]].drop_duplicates(["project_task"])

        for i in range(len(unique_list)):
            json_input = {"name": unique_list["project_task"].iloc[i].ljust(2, "_")
                , "estimate": unique_list["task_estimate"].iloc[i]
                          }

            response_tasks = self.post_call(endpoint="projects/" + unique_list["project_id"].iloc[i] + "/tasks",
                                            json_input=json_input)
            print(response_tasks)

    def createTimeEntries(self, timeEntries_json, ids_matching):

        for timeEntry in timeEntries_json:
            # print(timeEntry)
            if timeEntry["taskId"] in list(ids_matching["task_id_input"]):
                project_id = \
                ids_matching[ids_matching["task_id_input"] == timeEntry["taskId"]][["project_id_output"]].values[0][0]
                task_id = \
                ids_matching[ids_matching["task_id_input"] == timeEntry["taskId"]][["task_id_output"]].values[0][0]

                json_input = {
                    "billable": timeEntry["billable"],
                    "description": timeEntry["description"],
                    "projectId": project_id,
                    "taskId": task_id,
                    "end": timeEntry["timeInterval"]["end"],
                    "start": timeEntry["timeInterval"]["start"],
                    "tagsId": [],
                    "customFields": []

                }
                print(json.dumps(json_input, sort_keys=True, indent=4))
                response_tasks = self.post_call(endpoint="time-entries", json_input=json_input)