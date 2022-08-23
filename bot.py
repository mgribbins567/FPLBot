import requests
import json
import os
import discord

from dotenv import load_dotenv
from discord.ext import commands, tasks

from playerinfo import *
from printinfo import *
from constant import *


########################################
########## HISTORY HANDLER #############
########################################

def playerHistory(player_name):
    player_id = -1
    output_string = ""
    player_name = player_name.lower()

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name or i['web_name'].lower() == player_name:
            player_id = i['id']
            player_position = i['element_type']
            player_team = getTeam(i['team'])
            break
                         
    element_summary = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/")
    past_seasons = element_summary.json()['history_past']
    output_string += f"Current team: {player_team}\n----------\n"
    for i in past_seasons:
        if (i['season_name'] == '2021/22' or i['season_name'] == '2020/21'):
            output_string += printPlayerHistory(i, player_position)

    if (output_string == ""):
        output_string = "Player has not played in the past 2 seasons\n"

    fixture_list = requests.get("https://draft.premierleague.com/api/draft/83867/choices")
    for i in fixture_list.json()['choices']:
        if player_id == i['element']:
            drafted_by_first = i['player_first_name']
            drafted_by_last = i['player_last_name']
            pick_num = i['pick']
            round_num = i['round']
            output_string += f"----------\nPicked by {drafted_by_first} {drafted_by_last}\nPicked at round {round_num} pick {pick_num}\n----------\n"
            break
        
    
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
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name or i['web_name'].lower() == player_name:
            output_string = printPlayerRank(i)
            break

    if (output_string == ""):
        output_string = "Player does not exist or has not been given a ranking yet"

    return output_string


########################################
########### MATCH HANDLER ##############
########################################

def matchSearch(team_h, team_a):
    output_string = ''
    team_h = getTeamCode(team_h)
    team_a = getTeamCode(team_a)
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        if (i['team_h'] == team_h and i['team_a'] == team_a):
            output_string = printFixtureInfo(i)
            return output_string
    output_string = 'Match cannot be found'
    return output_string

########################################
########## MATCHDAY HANDLER ############
########################################

def matchdaySearch():
    output_string = ''
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        if (kickoff_time.month == datetime.now().month and kickoff_time.day == datetime.now().day):
            output_string += printFixtureInfoAbbreviated(i)

    if output_string == '':
        output_string = 'No matches today'

    return output_string

########################################
########## GAMEWEEK HANDLER ############
########################################

def gameweekSearch():
    output_string = ''
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        if (i['event'] == gameweek_number):
            output_string += printFixtureInfoAbbreviated(i)
    return output_string

########################################
########### STATS HANDLER ##############
########################################

def playerStats(player_name):
    player_id = -1
    output_string = ""
    player_name = player_name.lower()
    player_team = ''
    player_position = 0
    player_position_str = ''

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if getAdjustedPlayerName(i['web_name'].lower()) == player_name or i['web_name'].lower() == player_name:
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

    if output_string == '':
        output_string = 'Player cannot be found'

    owner = getPlayerOwner(player_id)
    output_string += f"----------\nOwned by {owner}"

    return output_string

########################################
############ TEAM HANDLER ##############
########################################

def managerTeam(manager_name):
    output_string = ''
    counter = 0
    manager_id = getManagerID(manager_name)
    points = getManagerEventPoints(manager_id)
    total_points = getManagerOverallPoints(manager_id)
    average_points = str(round(total_points/gameweek_number,2))
    output_string += f"Current Points: {points} | Average Points: {average_points}\n\n"

    

    player_list = requests.get(f"https://draft.premierleague.com/api/entry/{manager_id}/event/{gameweek_number}")
    player_list = player_list.json()
    for i in player_list['picks']:
        if (counter == 11):
            output_string += '-----SUBS-----\n'
        output_string += printManagerTeam(i)
        counter += 1



    return output_string

########################################
############# VS HANDLER ###############
########################################

def managerVS(manager_name):
    output_string = ''
    manager_id = 0
    if (manager_name != ''):
        manager_id = getManagerEntryID(manager_name)

    match_list = requests.get("https://draft.premierleague.com/api/league/83867/details")
    match_list = match_list.json()
    for i in match_list['matches']:
        if ((i['league_entry_1'] == manager_id or i['league_entry_2'] == manager_id) and i['event'] == gameweek_number) or (manager_name == '' and i['event'] == gameweek_number):
            output_string += printVS(i)

    return output_string

########################################
########### LEAGUE HANDLER #############
########################################

def leagueStandings():
    output_string = ''

    standings = requests.get("https://draft.premierleague.com/api/league/83867/details")
    standings = standings.json()
    for i in standings['standings']:
        output_string += printStandings(i)

    return output_string

########################################
######## FIXTURE ALERT HANDLER #########
########################################

def fixtureAlert():
    output_string = ''
    est = pytz.timezone('US/Eastern')
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    fixture_list = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    for i in fixture_list.json():
        kickoff_time = i['kickoff_time'].replace('T', ' ',)
        kickoff_time = kickoff_time.replace('Z', '',)
        kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
        kickoff_time = pytz.utc.localize(kickoff_time)
        kickoff_time = kickoff_time.astimezone(est)
        alert_time = kickoff_time - timedelta(minutes=60)
        if (kickoff_time.month == datetime.now().month and kickoff_time.day == datetime.now().day):
            current_time = datetime.now().astimezone(est)
            if (alert_time <= current_time <= kickoff_time and i['code'] not in alert_list):
                team_h = getTeam(i['team_h'])
                team_a = getTeam(i['team_a'])
                alert_list.append(i['code'])
                output_string += f"{team_h} vs {team_a} starts in the next hour!\n"
    role_string = "<@&1004944905208078479>\n"
    if output_string != '':
        output_string = role_string + output_string
    return output_string

########################################
############ BOT HANDLER ###############
########################################

gameweek_number = 3

alert_list = []

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

########################################
########### PLAYER LOOKUPS #############
########################################

@bot.command(name='history', help='#player-lookups Responds with the 2020/21 and 2021/22 stats of the player entered')
async def history(ctx, name: str):
    if (ctx.channel.id == PLAYERLOOKUPS):
        response = playerHistory(name.lower())
        await ctx.send(response)

@bot.command(name='rank', help='#player-lookups Responds with the rankings of the player entered')
async def rank(ctx, name: str):
    if (ctx.channel.id == PLAYERLOOKUPS):
        response = playerRank(name.lower())
        await ctx.send(response)

@bot.command(name='stats', help='#player-lookups Responds with the current season stats of the player entered')
async def stats(ctx, name: str):
    if (ctx.channel.id == PLAYERLOOKUPS):
        response = playerStats(name.lower())
        await ctx.send(response)

@bot.command(name='team', help='#player-lookups #league-lookups Responds with the current team of the manager name entered')
async def team(ctx, name: str):
    if (ctx.channel.id == PLAYERLOOKUPS or ctx.channel.id == LEAGUELOOKUPS):
        response = managerTeam(name.lower())
        await ctx.send(response)

########################################
########### MATCH LOOKUPS ##############
########################################

@bot.command(name='match', help='#match-lookups Responds with the match stats for the match entered')
async def match(ctx, team_h: str, team_a: str):
    if (ctx.channel.id == MATCHLOOKUPS):
        response = matchSearch(team_h, team_a)
        await ctx.send(response)

@bot.command(name='matchday', help='#match-lookups Responds with details of all matches on the current day')
async def matchday(ctx):
    if (ctx.channel.id == MATCHLOOKUPS):
        response = matchdaySearch()
        await ctx.send(response)

@bot.command(name='gameweek', help='#match-lookups Responds with details of all matches during the gameweek')
async def gameweek(ctx):
    if (ctx.channel.id == MATCHLOOKUPS):
        print('command works')
        response = gameweekSearch()
        await ctx.send(response)

########################################
########### LEAGUE LOOKUPS #############
########################################

@bot.command(name='vs', help='#league-lookups Responds with the current gameweek matchup for the manager')
async def vs(ctx, name=''):
    if (ctx.channel.id == LEAGUELOOKUPS):
        response = managerVS(name)
        await ctx.send(response)

@bot.command(name='league', help='#league-lookups Responds with the current league standings')
async def vs(ctx):
    if (ctx.channel.id == LEAGUELOOKUPS):
        response = leagueStandings()
        await ctx.send(response)

########################################
############## GENERAL #################
########################################

@bot.command(name='tottenham', help='shit')
async def tottenham(ctx):
    if (ctx.channel.id == GENERAL):
        response = 'shit'
        await ctx.send(response)

@bot.command(name='shit', help='tottenham')
async def tottenham(ctx):
    if (ctx.channel.id == GENERAL):
        response = 'tottenham'
        await ctx.send(response)



@tasks.loop(minutes = 5)
async def alerts():
    message_channel = bot.get_channel(MATCHLOOKUPS)
    response = fixtureAlert()
    if (response != ''):
        await message_channel.send(response)

@alerts.before_loop
async def before():
    await bot.wait_until_ready()

alerts.start()

bot.run(TOKEN)

