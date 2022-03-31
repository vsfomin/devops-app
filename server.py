from flask import Flask, render_template, request
import get_nhl_data
import db_methods

app = Flask(__name__)
cur, conn = db_methods.db_connect()

@app.route('/')
@app.route('/<month>')
def index(month=None):
  start_date, end_date = get_nhl_data.get_start_and_end_date(month=month)
  games, players = db_methods.get_data_from_db(cur, start_date, end_date)
  if not games and not players:
    url = f"https://statsapi.web.nhl.com/api/v1/schedule?teamId=19&startDate={start_date}&endDate={end_date}"
    all_games_dict, all_stlouis_links, all_stlouis_games_list, games_in_particular_city, all_players = get_nhl_data.main(url)
    db_methods.insert_data_to_db(all_stlouis_games_list, all_players, cur, conn)
    games, players = db_methods.get_data_from_db(cur, start_date, end_date)
  return render_template('index.html', games=games, players=players, month=month)

if __name__ == '__main__':
  app.run(debug=True)