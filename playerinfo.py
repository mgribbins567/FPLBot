import requests
import json
import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

def getAdjustedPlayerName(player_name):
    player_name = player_name.replace('ü', 'u',)
    player_name = player_name.replace('é', 'e',)
    player_name = player_name.replace('ø', 'o',)
    player_name = player_name.replace('š', 's',)
    player_name = player_name.replace('ć', 'c',)
    player_name = player_name.replace('á', 'a',)
    player_name = player_name.replace('ã', 'a',)
    player_name = player_name.replace('í', 'i',)
    player_name = player_name.replace('A.', '',)
    player_name = player_name.replace('ó', 'o',)
    player_name = player_name.replace('ï', 'i',)
    player_name = player_name.replace('ä', 'a',)
    player_name = player_name.replace('ö', 'o',)
    player_name = player_name.replace('ß', 'ss',)
    player_name = player_name.replace(' ', '',)
    return player_name

def getTeam(team_number):
    team_info = requests.get("https://draft.premierleague.com/api/bootstrap-static")
    team_info = team_info.json()
    for i in team_info['teams']:
        if team_number == i['id']:
            return i['name']
    
def getTeamCode(team_abbr):
    team_info = requests.get("https://draft.premierleague.com/api/bootstrap-static")
    team_info = team_info.json()
    for i in team_info['teams']:
        if team_abbr == i['short_name'].lower():
            return i['id']

def getPlayer(element):
    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if i['id'] == element:
            return i['web_name']

def getPlayerPositionID(player_id):
    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if i['id'] == player_id:
            return i['element_type']

def getPlayerPosition(position_id):
    if position_id == 1:
        return 'GKP'
    elif position_id == 2:
        return 'DEF'
    elif position_id == 3:
        return 'MID'
    elif position_id == 4:
        return 'FWD'

def getManagerID(name):
    manager = {
        'matthew':353779,
        'amanda':385370,
        'andrew':356128,
        'darryan':354022,
        'scott':385439,
        'joshua':357590,
        'jake':378019,
        'ricky':378036,
        'matthewr':356133,
        'kevin':381271,
        'carson':384273,
        'dylan':356402,
        'jesse':354097,
        'zach':385315,
        'emily':385811,
        'stephen':381537
        }
    return manager.get(name,0)

def getManagerEntryID(name):
    manager = {
        'matthew':355184,
        'amanda':387336,
        'andrew':357575,
        'darryan':355430,
        'scott':387405,
        'joshua':359054,
        'jake':379767,
        'ricky':379785,
        'matthewr':357580,
        'kevin':383101,
        'carson':386207,
        'dylan':357852,
        'jesse':355507,
        'zach':387281,
        'emily':387791,
        'stephen':383374
        }
    return manager.get(name,0)

def getManagerName(id):
    manager = {
        353779:'Matthew',
        385370:'Amanda',
        356128:'Andrew',
        354022:'Darryan',
        385439:'Scott',
        357590:'Joshua',
        378019:'Jake',
        378036:'Ricky',
        356133:'MatthewR',
        381271:'Kevin',
        384273:'Carson',
        356402:'Dylan',
        354097:'Jesse',
        385315:'Zach',
        385811:'Emily',
        381537:'Stephen'
        }
    return manager.get(id,'nobody')

def getManagerEntryName(name):
    manager = {
        355184:'Matthew',
        387336:'Amanda',
        357575:'Andrew',
        355430:'Darryan',
        387405:'Scott',
        359054:'Joshua',
        379767:'Jake',
        379785:'Ricky',
        357580:'MatthewR',
        383101:'Kevin',
        386207:'Carson',
        357852:'Dylan',
        355507:'Jesse',
        387281:'Zach',
        387791:'Emily',
        383374:'Stephen'
        }
    return manager.get(name,0)

def getPlayerOwner(player_id):
    owner = ''

    player_list = requests.get("https://draft.premierleague.com/api/league/83867/element-status") 
    player_list = player_list.json()
    for i in player_list['element_status']:
        if player_id == i['element']:
            return getManagerName(i['owner'])

    owner = 'nobody'
    return owner

def getManagerEventPoints(manager_id):
    event_stats = requests.get(f"https://draft.premierleague.com/api/entry/{manager_id}/public")
    event_stats = event_stats.json()
    return event_stats['entry']['event_points']

def getManagerOverallPoints(manager_id):
    event_stats = requests.get(f"https://draft.premierleague.com/api/entry/{manager_id}/public")
    event_stats = event_stats.json()
    return event_stats['entry']['overall_points']
