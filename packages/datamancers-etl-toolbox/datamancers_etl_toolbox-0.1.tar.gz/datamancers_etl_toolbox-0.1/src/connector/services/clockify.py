import requests
import json
import pandas as pd
import logging
import sys
import datamonk.utils.functions  as utls

logger=logging.getLogger(__name__)

class instance():
    def __init__(self,workspace_id,token):

        self.headers = {"X-Api-Key":token,'Content-Type': 'application/json'}
        self.endpoint_basic="https://api.clockify.me/api/v1/workspaces/"+workspace_id+"/"
        self.endpoint_user="https://api.clockify.me/api/v1/user"
        self.workspace_id = workspace_id


        try:
            res=requests.get(self.endpoint_user,headers=self.headers)
            self.user=res.json()["email"]
            logger.info("instance for user "+ self.user +" in workspace "+ self.workspace_id +" initialized succesfully")
            self.workspaces=requests.get("https://api.clockify.me/api/v1/workspaces",headers=self.headers).json()

        except Exception as e:
            logger.error("instance unsuccessful, error message:"+str(e))

    def __get_call(self,endpoint,params=""):
        response_text = requests.get(self.endpoint_basic + endpoint + "/", headers=self.headers, params=params)
        response_json=json.loads(response_text.text)
        return response_json
    
    def getProjects(self):
        response_projects=self.__get_call(endpoint="projects",params={"page-size":5000})
        pd_projects=pd.DataFrame([(i["id"],i["name"],i["clientId"],i["color"]) for i in response_projects],
                                 columns=["project_id","project_name","client_id","color"]
                                 )
        pd_projects["project_name"] = pd_projects["project_name"].str.ljust(2, "_")
        return pd_projects

    def getTimeEntries(self,start,end):
        params={"start":start,"end":end,"page-size":500}
        response_timeEntries=self.__get_call(endpoint="/user/"+self.getUserId()+"/time-entries",params=params)
        logger.info("fetched time entries for date range " + start + " - " + end
            )
        return response_timeEntries

    def getReports(self,start,end,report_type='detailed'):
        self.endpoint_basic="https://reports.api.clockify.me/v1"
        endpoint = "/workspaces/" + self.workspace_id + "/reports/" + report_type
        params = {"dateRangeStart": start, "dateRangeEnd": end,"detailedFilter": {
                      "page": 1,
                      "pageSize": 1000}
                  }
        total=0
        records_processed=0

        while  records_processed < total or params["detailedFilter"]['page']== 1:
            output = self.__post_call(endpoint=endpoint, params=params)

            if output.status_code == 200:
                logger.info(f"fetched report for date range {start} - {end} with page {params['detailedFilter']['page']}")
                if params["detailedFilter"]['page']==1:
                    data=output.json()
                    total = data['totals'][0]["entriesCount"]
                else:
                    data["timeentries"]=data["timeentries"]+output.json()["timeentries"]
                records_processed = min(params["detailedFilter"]['page'] * params["detailedFilter"]['pageSize'], total)
                params["detailedFilter"]['page']+=1
            elif output.status_code  >= 400:
                raise Exception(f"error with status code: {output.status_code} and error reason: {output.reason}")
        return data
    
    def getClients(self):
        response_clients=self.__get_call(endpoint="clients",params={"page-size":5000})
        pd_clients=pd.DataFrame([(i["id"],i["name"]) for i in response_clients],columns=["client_id","client_name"])    
        return pd_clients

    def getUserId(self):
        response_text = requests.get(self.endpoint_user,headers=self.headers)
        response_json=json.loads(response_text.text)["id"]
        return response_json
            
    def getTasks(self):
        pd_tasks_columns=["task_id","task_name","project_id","task_estimate","task_duration","task_status"]
        pd_tasks=pd.DataFrame(columns=pd_tasks_columns)
        pd_projects=self.getProjects()
        for projectId in list(pd_projects["project_id"]):
            response_task=self.__get_call(endpoint="projects/"+projectId+"/tasks",params={"page-size":5000})
            pd_task = pd.DataFrame([(task["id"],task["name"],task["projectId"],
                                     task["estimate"],task["duration"],task["status"]
                                     ) for task in response_task],columns=pd_tasks_columns
                                   )
            pd_tasks=pd.concat([pd_tasks,pd_task])
        return pd_tasks


    def getAllWorkspaceElements(self):

        projects=self.getProjects()
        clients=self.getClients()
        tasks=self.getTasks()
        workspace_elements=clients.merge(projects.merge(tasks,on="project_id",how="left"),on="client_id",how="left")
        workspace_elements["sync_id"] = (workspace_elements["project_name"] + "|" + workspace_elements["task_name"])
        return workspace_elements
    
    def __post_call(self,endpoint,params):
        try:
            request_call= requests.post(self.endpoint_basic+endpoint+"/",json=params,headers=self.headers)
        except requests.exceptions.RequestException as e:  
            raise Exception(e)
        return request_call

    def createProjects(self,projectSetup_list,client_id):
        unique_list=projectSetup_list[["client_name","color"]].drop_duplicates(["client_name"])
        list_len=len(unique_list)
        for i in range(list_len):
            project_name = unique_list["client_name"].iloc[i].ljust(2,"_")
            json_input = {"name":project_name
                          ,"clientId":client_id
                          ,"billable":"true"
                          ,"isPublic":"false"
                          ,"color":unique_list["color"].iloc[i]
                          }
            self.__post_call(endpoint="projects",json_input=json_input)
            logger.info("project element "+ project_name +" added to client_id"+ client_id +"in workspace "+ self.workspace_id +"\noutput:"+ json_input)
        logger.info("all projects created results: %s",list_len)
    def createTasks(self,taskSetup_list):
        unique_list=taskSetup_list[["project_id","project_task","task_estimate"]].drop_duplicates(["project_task"])
        tasks_len=len(taskSetup_list)

        if tasks_len > 0:
            for i in range(len(unique_list)):
                task_element_name=unique_list["project_task"].iloc[i].ljust(2, "_")
                json_input = {"name":task_element_name
                              ,"estimate":unique_list["task_estimate"].iloc[i]
                              }

                self.__post_call(endpoint="projects/"+unique_list["project_id"].iloc[i]+"/tasks",json_input=json_input)
                logger.info("task element "
                                                        + task_element_name +
                                                        " added to workspace "
                                                        + self.workspace_id +
                                              "output: %s",json_input
                                     )

            logger.info("all tasks created. results: %s",tasks_len)


    def createTimeEntries(self,timeEntries_json,ids_matching):
        results=0
        for timeEntry in timeEntries_json:

            if timeEntry["taskId"] in list(ids_matching["task_id_input"]):
                results+=1
                project_id=ids_matching[ids_matching["task_id_input"]==timeEntry["taskId"]][["project_id_output"]].values[0][0]
                task_id=ids_matching[ids_matching["task_id_input"]==timeEntry["taskId"]][["task_id_output"]].values[0][0]
                
                json_input={
                              "billable": timeEntry["billable"],
                              "description": timeEntry["description"],
                              "projectId": project_id,
                              "taskId": task_id,
                              "end": timeEntry["timeInterval"]["end"],
                              "start": timeEntry["timeInterval"]["start"],
                              "tagsId":[],
                              "customFields":[]
                              
                            }
                json_output=json.dumps(json_input,sort_keys=True,indent=4)

                self.__post_call(endpoint="time-entries",json_input=json_input)
                logger.info("task "+ task_id+ " synced","output: %s",json_output)

        logger.info("all time entries created, results: %s",results)

