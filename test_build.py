import requests
import json
import os
import discord
import pytz
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from discord.ext import commands

from playerinfo import *
from printinfo import *


########################################
########## HISTORY HANDLER #############
########################################

def playerHistory(player_name):
    player_id = -1
    output_string = ""
    player_name = player_name.lower()

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name:
            player_id = i['id']
            player_position = i['element_type']
            player_team = getTeam(i['team'])
            break
        
    if (player_id != -1):                         
        element_summary = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/")
        past_seasons = element_summary.json()['history_past']
        #print(element_summary.json()['history'])
        print(f"Current team: {player_team}")
        for i in past_seasons:
            if (i['season_name'] == '2021/22' or i['season_name'] == '2020/21'):
                output_string += printPlayerHistory(i, player_position)

    fixture_list = requests.get("https://draft.premierleague.com/api/draft/83867/choices")
    for i in fixture_list.json()['choices']:
        if player_id == i['element']:
            drafted_by = i['player_first_name']
            pick_num = i['pick']
            round_num = i['round']
            output_string += f"----------\nPicked by {drafted_by}\nPicked at {round_num}/{pick_num}\n----------\n"
            break
        
    if (output_string == ""):
        output_string = "Player does not exist or has not played in the past 2 seasons"
    return output_string

########################################
############ RANK HANDLER ##############
########################################

def playerRank(player_name):
    player_code = -1
    output_string = ""
    player_name = player_name.lower()

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name:
            output_string = printPlayerRank(i)
            break

    if (output_string == ""):
        output_string = "Player does not exist or has not been given a ranking yet"

    return output_string
    

def leagueStandings():
    league_standing = requests.get("https://draft.premierleague.com/api/draft/83867/")
    print(league_standing.json())
    return

def fixtureAlert():
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        kickoff_time = kickoff_time.astimezone(est)
        alert_time = kickoff_time - timedelta(minutes=160)
        if (kickoff_time.month == datetime.now().month and kickoff_time.day == datetime.now().day):
            current_time = datetime.now().astimezone(est)
            if (alert_time <= current_time <= kickoff_time):
                output_string = "Game starts soon"
    return output_string

def match(team_h, team_a):
    team_h = getTeamCode(team_h)
    team_a = getTeamCode(team_a)
    print(team_h)
    print(team_a)
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        if (i['team_h'] == team_h and i['team_a'] == team_a):
            print('enters')
            output_string = printFixtureInfo(i)
            return output_string

def matchday():
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        if (kickoff_time.month == datetime.now().month and kickoff_time.day == datetime.now().day):
            output_string = printFixtureInfoAbbreviated(i)
            return output_string

def gameweekList():
    output_string = ''
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        if (i['event'] == gameweek):
            output_string += printFixtureInfoAbbreviated(i)
    return output_string

def fixtures(week):
    fantasy_fixtures = requests.get("https://draft.premierleague.com/api/league/83867/details")
    fantasy_fixtures = fantasy_fixtures.json()
    for i in fantasy_fixtures['matches']:
        #print(i)
        for j in i:
            print(j)
        #print(i['event'])
            if i['event'] == week:
                print(i['event'])

def stats(player_name):
    player_id = -1
    output_string = ""
    player_name = player_name.lower()
    player_team = ''
    player_position = 0
    player_position_str = ''

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name:
            player_id = i['id']
            player_position = i['element_type']
            player_team = getTeam(i['team'])
            break

    player_position_str = getPlayerPosition(player_position)
    output_string += f"{player_team} {player_position_str}\n"
    
    player_summary = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/")
    player_summary = player_summary.json()['history']
    for i in player_summary:
        output_string += printPlayerStats(i, player_position)

    owner = getPlayerOwner(player_id)
    output_string += f"Owned by {owner}"

    return output_string

def team_temp(manager_name):
    output_string = ''
    manager_id = getManagerID(manager_name)
        
    player_list = requests.get("https://draft.premierleague.com/api/league/83867/element-status") 
    player_list = player_list.json()
    for i in player_list['element_status']:
        if (i['owner'] == manager_id):
            output_string += printManagerTeam(i)
    
    return output_string

def team(manager_name):
    output_string = ''
    counter = 0

    manager_id = getManagerID(manager_name)

    player_list = requests.get(f"https://draft.premierleague.com/api/entry/{manager_id}/event/{gameweek}")
    player_list = player_list.json()
    for i in player_list['picks']:
        if (counter == 11):
            output_string += '----------\n'
        output_string += printManagerTeam(i)
        counter += 1

    return output_string

def vs(manager_name):
    output_string = ''
    manager_id = getManagerEntryID(manager_name)
    points = getManagerEventPoints(manager_id)
    output_string += f"Current Points: {points}\n"

    match_list = requests.get("https://draft.premierleague.com/api/league/83867/details")
    match_list = match_list.json()
    for i in match_list['matches']:
        if ((i['league_entry_1'] == manager_id or i['league_entry_2'] == manager_id) and i['event'] == gameweek):
            output_string = printVS(i)

    return output_string

    
def league():
    output_string = ''

    standings = requests.get("https://draft.premierleague.com/api/league/83867/details")
    standings = standings.json()
    for i in standings['standings']:
        output_string += printStandings(i)

    return output_string


gameweek = 3
name = ''
while (name != quit):
    print('Enter player name: ')
    name = input().lower()
    #response = fixtures(name)
    #response = playerHistory(name)
    #response = playerRank(name)
    #response = match('mun','bri')
    #response = gameweekList()
    #response = stats(name)
    response = team(name)
    #response = vs(name)
    #response = league()
#leagueStandings()
    print(response)
    
