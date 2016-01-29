#!/usr/bin/python

import praw
import feedparser
import soundcloud
import time
from apiclient.discovery import build
import json

with open('credentials.json', 'r') as credsFile:
    APIcredentials = json.load(credsFile)
with open('blacklist.json', 'r') as blacklistFile:
	blacklist = json.load(blacklistFile)

sc = soundcloud.Client(client_id=APIcredentials['credentials']['soundcloud'])

youtube = build('youtube', 'v3', developerKey=APIcredentials['credentials']['youtube'])
channel = youtube.channels().list(part='contentDetails', id='UCkbuz6q6G_u6AV9kCo3qDQw').execute()
videosPlaylistId = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

r = praw.Reddit('Im an automated poster, I post interesting stuff for /r/bromancerecords')
r.login('BMC_bot', APIcredentials['credentials']['reddit'], disable_warning=True)

def checkSC():
	scSubmissions = sc.get('/users/8600035/tracks', limit=20)
	toSubmit = []
	for x in range(len(scSubmissions)):
		toSubmit.append([scSubmissions[x].title, scSubmissions[x].permalink_url])
		for redditSubmission in r.get_subreddit('bromancerecords').get_new(limit=100):
			if redditSubmission.title == scSubmissions[x].title or redditSubmission.url == scSubmissions[x].permalink_url:
				toSubmit.remove([scSubmissions[x].title, scSubmissions[x].permalink_url])
		for y in range(len(blacklist['blacklist'])):
			if blacklist['blacklist'][y]['title'] == scSubmissions[x].title or blacklist['blacklist'][y]['url'] == scSubmissions[x].permalink_url:
				toSubmit.remove([scSubmissions[x].title, scSubmissions[x].permalink_url])
	return toSubmit

def checkYT():
	ytSubmissions = youtube.playlistItems().list(part="snippet", playlistId=videosPlaylistId, maxResults=30).execute()
	toSubmit = []
	for x in range(len(ytSubmissions)):
		toSubmit.append([ytSubmissions['items'][x]['snippet']['title'], 'https://www.youtube.com/watch?v={}'.format(ytSubmissions['items'][x]['snippet']["resourceId"]["videoId"])])
		for redditSubmission in r.get_subreddit('bromancerecords').get_new(limit=100):
			if redditSubmission.title == ytSubmissions['items'][x]['snippet']['title'] or redditSubmission.url == 'https://www.youtube.com/watch?v={}'.format(ytSubmissions['items'][x]['snippet']["resourceId"]["videoId"]):
				toSubmit.remove([ytSubmissions['items'][x]['snippet']['title'], 'https://www.youtube.com/watch?v={}'.format(ytSubmissions['items'][x]['snippet']["resourceId"]["videoId"])])
		for y in range(len(blacklist['blacklist'])):
			if blacklist['blacklist'][y]['title'] == ytSubmissions['items'][x]['snippet']['title'] or blacklist['blacklist'][y]['url'] == 'https://www.youtube.com/watch?v={}'.format(ytSubmissions['items'][x]['snippet']["resourceId"]["videoId"]):
				toSubmit.remove([ytSubmissions['items'][x]['snippet']['title'], 'https://www.youtube.com/watch?v={}'.format(ytSubmissions['items'][x]['snippet']["resourceId"]["videoId"])])
	return toSubmit


def checkTumblr():
	tumblrSubmissions = feedparser.parse('http://scrollingdownthestreets.tumblr.com/rss')
	toSubmit = []
	for x in range(len(tumblrSubmissions)):
		toSubmit.append([tumblrSubmissions.entries[x].title, tumblrSubmissions.entries[x].id])
		for redditSubmission in r.get_subreddit('bromancerecords').get_new(limit=100):
			if redditSubmission.title == tumblrSubmissions.entries[x].title or redditSubmission.url == tumblrSubmissions.entries[x].id:
				toSubmit.remove([tumblrSubmissions.entries[x].title, tumblrSubmissions.entries[x].id])
		for y in range(len(blacklist['blacklist'])):
			if blacklist['blacklist'][y]['title'] == tumblrSubmissions.entries[x].title or blacklist['blacklist'][y]['url'] == tumblrSubmissions.entries[x].id:
				toSubmit.remove([tumblrSubmissions.entries[x].title, tumblrSubmissions.entries[x].id])
	return toSubmit

def submit(title, url):
	r.submit('bromancerecords', title, url=url)

def jsonFormatting(scItems, ytItems, tItems):
	strJson = '{"blacklist": ['
	for item in scItems:
		strJson = strJson + '{"title": "' + str(item[0]) + '", "url": "' + str(item[1]) + '"},'
	for item in ytItems:
		strJson = strJson + '{"title": "' + str(item[0]) + '", "url": "' + str(item[1]) + '"},'
	for item in tItems:
		strJson = strJson + '{"title": "' + str(item[0]) + '", "url": "' + str(item[1]) + '"},'
	strJson = strJson[:-1] + ']}'
	return strJson

while True:
	for item in checkTumblr():
		submit(item[0], item[1])
	for item in checkSC():
		submit(item[0], item[1])
	for item in checkYT():
		submit(item[0], item[1])
	time.sleep(1000)
