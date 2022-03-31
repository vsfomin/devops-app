import requests
import json
import psycopg2
import datetime
import calendar
from dateutil.relativedelta import *
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import jinja2

# Script take all games from start date to end date, search game in St Louis (get_all_games_lisk_for_special_month() method), then enter to particular link
# for every game and get information about particular game (create_list_of_games_in_city_threads() method)
# After this script create two tables: one table repsesents date of the game and time on ice for every player, another table represents games in this city and scores for every game


def get_start_and_end_date(month=None):
    """
    Find the first and the last day of previous month
    Cound dates and return it for API requst usage
    """
    if not month:
        month = (datetime.datetime.now() - relativedelta(months=1)).strftime("%m")
    else:
        month = f"{datetime.datetime.strptime(month, '%B').month:02d}"
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d")
    cur_year, cur_month, cur_day = cur_date.split("-")
    first_day = f"{cur_year}-{month}-{str(calendar.monthrange(int(cur_year), int(month))[0])}"
    last_day = f"{cur_year}-{month}-{str(calendar.monthrange(int(cur_year), int(month))[1])}"
    return first_day, last_day


def get_some_parameters_from_response(path):
    """
    Метод делает Request по переданной ссылке и возвращает результат
    """
    payload={}
    headers = {}
    response = requests.request("GET", path, headers=headers, data=payload)
    result = json.loads(requests.request(          
             "GET",
             path,
             headers=headers,
             data=payload).text)
    return result

def get_all_games_lisk_for_special_month(all_games):
    """
    Method gets all links for St Louis games in particular month
    All of this links will be used in method create_list_of_games_in_city_threads
    """
    all_stlouis_links = []
    all_stlouis_games_list = []
    all_games_in_month_list = all_games['dates']
    for date in all_games_in_month_list:
        games_in_particular_date = date['games']
        for game in games_in_particular_date:
            try:
                if game['venue']['id'] == 5076:
                    all_stlouis_links.append(game['link'])
                    gamedate = game['gameDate'][:10]
                    away_team = game['teams']['away']['team']['name']
                    home_team = game['teams']['home']['team']['name']
                    scores = int(game['teams']['home']['score']) + int(game['teams']['away']['score'])           
                    all_stlouis_games_list.append([gamedate,away_team,home_team,scores])
            except:
                pass
    return all_stlouis_links, all_stlouis_games_list 

def create_list_of_games_in_city_threads(all_games_links):
    """
    Take links games in St. Louis and create list of
    """
    with ThreadPoolExecutor(max_workers=5) as ex:
        future_list = [ex.submit(get_some_parameters_from_response, f'https://statsapi.web.nhl.com/{link}') for link in all_games_links]
        all_games_in_stlouis = []
        for future in future_list:
            all_games_in_stlouis.append(future.result())
        return all_games_in_stlouis  
        
def create_all_players(games):
    """
    Create dict which contain all players parcitipated in all games in St Louis
    Contain name, date of game and time on ice in particular game
    """
    players_list = []
    result_dict = defaultdict(dict)
    for game in games:
        gamedate = game['gameData']['datetime']['dateTime'] 
        away_players = game['liveData']['boxscore']['teams']['away']['players']
        home_players = game['liveData']['boxscore']['teams']['home']['players']
        all_players = {**away_players, **home_players}
        for value in all_players.values():
            name = value['person']['fullName']
            if value['stats'].get('skaterStats'):
                timeOnIce = value['stats']['skaterStats']['timeOnIce']
                players_list.append([gamedate[:10], name, timeOnIce])
                result_dict[name].update({gamedate[0:10] : timeOnIce})
    return result_dict, players_list

def main(url):
    all_games_dict = get_some_parameters_from_response(url)
    all_stlouis_links = get_all_games_lisk_for_special_month(all_games_dict)[0]
    all_stlouis_games_list = get_all_games_lisk_for_special_month(all_games_dict)[1]
    games_in_particular_city = create_list_of_games_in_city_threads(all_stlouis_links) #list games in St. Louis  
    all_players = create_all_players(games_in_particular_city)[1]
    return all_games_dict, all_stlouis_links, all_stlouis_games_list, games_in_particular_city, all_players



# if __name__ == "__main__":

#    start_date = get_start_and_end_date()[0]
#    end_date = get_start_and_end_date()[1]      
#    url = f"https://statsapi.web.nhl.com/api/v1/schedule?teamId=19&startDate={start_date}&endDate={end_date}"
    
#    all_games_dict, all_stlouis_links, all_stlouis_games_list, games_in_particular_city, all_players = main(url)
#    cur, conn = db_connect()
#    insert_data_to_db(all_stlouis_games_list, all_players, cur, conn)
#    games, players = get_data_from_db(cur)

#    templateLoader = jinja2.FileSystemLoader('.')
#    templateEnv = jinja2.Environment(loader=templateLoader)
#    template_file = "index.tpl"
#    template = templateEnv.get_template(template_file)
#    html = template.render(games=games, players=players)
    
#     with open("/var/www/html/index.html", "w") as f:
#         f.write(html)

        