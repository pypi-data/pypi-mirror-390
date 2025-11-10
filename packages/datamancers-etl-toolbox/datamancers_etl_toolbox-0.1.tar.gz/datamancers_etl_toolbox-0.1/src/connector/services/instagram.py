# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 20:38:36 2020

@author: vitmr
"""

import instaloader
L = instaloader.Instaloader()
user = "vit_mrnavek"
password = "0gHR7s3HIDbJ"
L.login(user, password)
profile = instaloader.Profile.from_username(L.context, "doppiecoffee")

print(profile.followees) #number of following
print(profile.followers) #number of followers
print(profile.full_name) #full name
print(profile.biography) #bio
print(profile.profile_pic_url)  #profile picture url 
print(profile.get_posts()) #list of posts
print(profile.get_followers()) #list of followers
print(profile.get_followees()) #list of followees

for post in profile.get_posts():
    #print(post.likes)
    #print(post.url)
    for comment in post.get_comments():
        print(post.comments)
