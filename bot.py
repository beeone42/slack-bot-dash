#!/usr/bin/python

import time, json, os, requests, urllib, subprocess
from slackclient import SlackClient

def read_config(confname):
    with open(confname) as json_data_file:
        data = json.load(json_data_file)
    return (data)

def find_user_name(sc, uid):
    users = json.loads(sc.api_call("users.list"))
    for user in users['members']:
        if (user['id'] == uid):
            return (user['name'])

def find_group_id(sc, name):
    groups = json.loads(sc.api_call("groups.list"))
    for grp in groups['groups']:
        if (grp['name'] == name):
            return (grp['id'])

def find_channel_id(sc, name):
    channels = json.loads(sc.api_call("channels.list"))
    for chan in channels['channels']:
        if (chan['name'] == name):
            return (chan['id'])

def post_msg(msg):
    global config
    sc.server.channels.find(config['group']).send_message(str(msg))

def msg_open(sc, msg):
    global config
    r = requests.get(config['open_door_base'] + msg[1])
    post_msg(r.content)

# {u'text': u'salut', u'ts': u'1437998018.000013', u'user': u'U03BC35LH', u'team': u'T03BDS0E2', u'type': u'message', u'channel': u'D086XDSTF'}
def rtm_message(sc, rtm):
    global config
    if (rtm["channel"] == config['chan']):
        rtm["username"] = find_user_name(sc, rtm["user"])
        print rtm["username"] + ": " + rtm["text"]

funcdict = {
    'message': rtm_message
}

config = read_config("config.json")
sc = SlackClient(config['token'])
config['chan'] = find_channel_id(sc, config['channel'])
print(config['chan'])

if sc.rtm_connect():
    while True:
        rtm = sc.rtm_read()
        try:
            if (len(rtm) > 0):
                for r in rtm:
                    if "type" in r:
                        if r["type"] in funcdict.keys():
                            funcdict[r["type"]](sc, r)
        except Exception:
            print("parse error: ")
            print(rtm)
            pass
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
