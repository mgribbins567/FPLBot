from turtle import position
import requests
import json
import os
import discord
import pytz
from datetime import datetime, timedelta

from dotenv import load_dotenv
from discord.ext import commands

from playerinfo import *

def printPlayerHistory(player_history, player_position):
    season_name = player_history['season_name']
    total_points = player_history['total_points']
    minutes = player_history['minutes']
    if (minutes != 0):
        points_per_minute = str(round(90*(total_points/minutes),2))
    else:
        points_per_minute = 0
    goals = player_history['goals_scored']
    assists = player_history['assists']
    clean_sheets = player_history['clean_sheets']
    goals_conceded = player_history['goals_conceded']
    own_goals = player_history['own_goals']
    pen_saved = player_history['penalties_saved']
    pen_missed = player_history['penalties_missed']
    yellows = player_history['yellow_cards']
    reds = player_history['red_cards']
    saves = player_history['saves']
    bonus = player_history['bonus']
    bps = player_history['bps']
    influence = player_history['influence']
    creativity = player_history['creativity']
    threat = player_history['threat']
    ict_index = player_history['ict_index']
    if (player_position == 1):
        output_string = f"{season_name}\n----------\nPosition: GK\nMinutes: {minutes}\nTotal Points: {total_points}\nPoints Per 90 Minutes: {points_per_minute}\nClean Sheets: {clean_sheets}\nGoals Conceded: {goals_conceded}\nOwn Goals: {own_goals}\nPenalties Saved: {pen_saved}\nYellow Cards: {yellows}\nRed Cards: {reds}\nSaves: {saves}\nBonus Points: {bonus}\nTotal BPS: {bps}\n"
    elif (player_position == 2):
        output_string = f"{season_name}\n----------\nPosition: DEF\nMinutes: {minutes}\nTotal Points: {total_points}\nPoints Per 90 Minutes: {points_per_minute}\nGoals: {goals}\nAssists: {assists}\nClean Sheets: {clean_sheets}\nGoals Conceded: {goals_conceded}\nOwn Goals: {own_goals}\nYellow Cards: {yellows}\nRed Cards: {reds}\nBonus Points: {bonus}\nTotal BPS: {bps}\n"
    elif (player_position == 3):
        output_string = f"{season_name}\n----------\nPosition: MID\nMinutes: {minutes}\nTotal Points: {total_points}\nPoints Per 90 Minutes: {points_per_minute}\nGoals: {goals}\nAssists: {assists}\nClean Sheets: {clean_sheets}\nOwn Goals: {own_goals}\nPenalties Missed: {pen_missed}\nYellow Cards: {yellows}\nRed Cards: {reds}\nBonus Points: {bonus}\nTotal BPS: {bps}\n"
    elif (player_position == 4):
        output_string = f"{season_name}\n----------\nPosition: FWD\nMinutes: {minutes}\nTotal Points: {total_points}\nPoints Per 90 Minutes: {points_per_minute}\nGoals: {goals}\nAssists: {assists}\nOwn Goals: {own_goals}\nPenalties Missed: {pen_missed}\nYellow Cards: {yellows}\nRed Cards: {reds}\nBonus Points: {bonus}\nTotal BPS: {bps}\n"
    return output_string

def printPlayerRank(player_details):
    player_position = player_details['element_type']
    if (player_position == 1):
        player_position_string = 'GK'
    elif (player_position == 2):
        player_position_string = 'DEF'
    elif (player_position == 3):
        player_position_string = 'MID'
    elif (player_position == 4):
        player_position_string = 'FWD'
    player_team = getTeam(player_details['team'])
    influence = player_details['influence_rank_type']
    creativity = player_details['creativity_rank_type']
    threat = player_details['threat_rank_type']
    ict = player_details['ict_index_rank_type']
    influence_overall = player_details['influence_rank']
    creativity_overall = player_details['creativity_rank']
    threat_overall = player_details['threat_rank']
    ict_overall = player_details['ict_index_rank']
    output_string = f"Rank as {player_team} {player_position_string}:\nInfluence: {influence}\nCreativity: {creativity}\nThreat: {threat}\nOverall: {ict}\n"
    output_string += f"\nRank Overall:\nInfluence: {influence_overall}\nCreativity: {creativity_overall}\nThreat: {threat_overall}\nOverall: {ict_overall}\n"
    return output_string

def printFixtureInfo(fixture_details):
    bps = 0
    est = pytz.timezone('US/Eastern')
    fmt = '%m/%d/%y %H:%M:%S %Z'
    output_string = ''
    team_h = getTeam(fixture_details['team_h'])
    team_a = getTeam(fixture_details['team_a'])
    team_h_score = fixture_details['team_h_score']
    team_a_score = fixture_details['team_a_score']
    kickoff_time = fixture_details['kickoff_time'].replace('T', ' ',)
    kickoff_time = kickoff_time.replace('Z', '',)
    kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
    kickoff_time = pytz.utc.localize(kickoff_time)
    kickoff_time = kickoff_time.astimezone(est).strftime(fmt)
    stats = ''
    for i in fixture_details['stats']:
        if i['identifier'] == 'bps':
            bps = 1
        stats += '\n' + i['identifier'].replace('_', ' ',).capitalize() + ':\n'
        if i['a']:
            for j in i['a']:
                value = j['value']
                player = getPlayer(j['element'])
                if not bps:
                    stats += player + ': ' + str(value) + '\n'
                else:
                    stats += player + ' ' + str(value) + ','
        if bps:
            stats = stats.rstrip(stats[-1])
        if i['h']:
            if bps:
                stats += '\n'
            for j in i['h']:
                value = j['value']
                player = getPlayer(j['element'])
                if not bps:
                    stats += player + ': ' + str(value) + '\n'
                else:
                    stats += player + ' ' + str(value) + ','
        if bps:
            stats = stats.rstrip(stats[-1])
    
    if stats != '':
        stats += '\n----------\n'
    output_string += f"{team_h} ({team_h_score}) - {team_a} ({team_a_score})\n----------\nKickoff Time: {kickoff_time}\n----------{stats}"
    return output_string

def printFixtureInfoAbbreviated(fixture_details):
    est = pytz.timezone('US/Eastern')
    fmt = '%m/%d/%y %H:%M:%S %Z'
    output_string = ''
    team_h = getTeam(fixture_details['team_h'])
    team_a = getTeam(fixture_details['team_a'])
    team_h_score = fixture_details['team_h_score']
    team_a_score = fixture_details['team_a_score']
    kickoff_time = fixture_details['kickoff_time'].replace('T', ' ',)
    kickoff_time = kickoff_time.replace('Z', '',)
    kickoff_time = datetime.strptime(kickoff_time, '%Y-%m-%d %H:%M:%S')
    kickoff_time = pytz.utc.localize(kickoff_time)
    kickoff_time = kickoff_time.astimezone(est).strftime(fmt)
    output_string += f"{team_h} ({team_h_score}) - {team_a} ({team_a_score})\nKickoff Time: {kickoff_time}\n----------\n"
    return output_string

def printPlayerStats(player_details, player_position):
    output_string = '----------\n'
    opponent_team = getTeam(player_details['opponent_team'])
    minutes = player_details['minutes']
    team_h_score = player_details['team_h_score']
    team_a_score = player_details['team_a_score']
    was_home = player_details['was_home']
    points = player_details['total_points']
    goals_scored = player_details['goals_scored']
    assists = player_details['assists']
    clean_sheets = player_details['clean_sheets']
    goals_conceded = player_details['goals_conceded']
    own_goals = player_details['own_goals']
    pen_saved = player_details['penalties_saved']
    pen_missed = player_details['penalties_missed']
    yellows = player_details['yellow_cards']
    reds = player_details['red_cards']
    saves = player_details['saves']
    bonus = player_details['bonus']
    bps = player_details['bps']

    if (was_home):
        output_string += f"vs {opponent_team} ({team_h_score}) - ({team_a_score})\n"
    else:
        output_string += f"at {opponent_team} ({team_a_score}) - ({team_h_score})\n"

    output_string += f"Mins: {minutes}\n"
    output_string += f"Score: {points}"
    if (goals_scored):
        output_string += f" | G: {goals_scored}"
    if (assists):
        output_string += f" | A: {assists}"
    if (own_goals):
        output_string += f" | OG: {own_goals}"
    if (player_position != 4):
        if (clean_sheets):
            output_string += f" | CS: {clean_sheets}"
        output_string += f" | GC: {goals_conceded}"
    if (pen_saved):
        output_string += f" | PS: {pen_saved}"
    if (pen_missed):
        output_string += f" | PM: {pen_missed}"
    if (saves):
        output_string += f" | S: {saves}"
    if (yellows):
        output_string += f" | Y: {yellows}"
    if (reds):
        output_string += f" | R: {reds}"
    if (bonus):
        output_string += f"\nBonus: {bonus} | BPS: {bps}"
    else:
        output_string += f"\nBPS: {bps}"
    output_string += "\n"

    return output_string
    

def printManagerTeam(player_details):
    output_string = ''
    player_position = ''
    player_team = ''
    player_name = getPlayer(player_details['element'])
    player_id = player_details['element']

    static_elements = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    for i in (static_elements.json()['elements']):
        if i['id'] == player_id:
            player_position =  getPlayerPosition(i['element_type'])
            player_team = getTeam(i['team'])
            points = i['event_points']
            break

    output_string += f"{player_position} | {player_team} | {player_name} | {points}\n"

    return output_string


def printVS(fixture_details):
    output_string = ''
    manager_1 = getManagerEntryName(fixture_details['league_entry_1'])
    manager_2 = getManagerEntryName(fixture_details['league_entry_2'])
    #manager_1_score = fixture_details['league_entry_1_points']
    manager_1_score = str(getManagerEventPoints(getManagerID(getManagerEntryName(fixture_details['league_entry_1']).lower())))
    #manager_2_score = fixture_details['league_entry_2_points']
    manager_2_score = str(getManagerEventPoints(getManagerID(getManagerEntryName(fixture_details['league_entry_2']).lower())))

    output_string += f"{manager_1} {manager_1_score} vs {manager_2_score} {manager_2}\n"

    return output_string

def printStandings(position_details):
    output_string = ''

    rank = position_details['rank']
    last_rank = position_details['last_rank']
    manager_name = getManagerEntryName(position_details['league_entry'])
    wins = position_details['matches_won']
    draws = position_details['matches_drawn']
    losses = position_details['matches_lost']
    points_for = position_details['points_for']
    points_against = position_details['points_against']
    points_difference = points_for - points_against

    output_string += f"{rank} ({last_rank}) | {manager_name} | {wins} - {draws} - {losses} | {points_for} - {points_against} "
    if (points_difference > 0):
        output_string += f"/ +{points_difference}\n"
    else:
        output_string += f"/ {points_difference}\n"

    return output_string

