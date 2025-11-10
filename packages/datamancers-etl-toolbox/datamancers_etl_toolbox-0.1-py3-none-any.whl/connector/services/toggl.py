# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 01:03:40 2021

@author: vitmr
"""

from toggl.api_client import TogglClientApi

settings = {
    'token': 'ba8ad9cf4ca8ea8c29d6dafedac8bbd6'
    ,'user_agent': 'timeEntrySaver'
}
toggle_client = TogglClientApi(settings)

response = toggle_client.get_workspaces()

TogglClientApi()

from toggl.TogglPy import Toggl

toggl = Toggl()
toggl.setAPIKey('ba8ad9cf4ca8ea8c29d6dafedac8bbd6') 
print(toggl.getWorkspaces())
print(toggl.getClients())

toggl.getClientProjects()