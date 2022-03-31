
import psycopg2

def checkTableExists(dbcon, tablename):
    """
    Check if table exist in DB
    """
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def change_time_format(time):
    """
    Change time format when we insert players into
    postgres
    """
    time = time.split(':')
    time[0] = time[0]+' minutes'
    time[1] = time[1]+' seconds'
    time = ' '.join(time)
    return time

def db_connect():
    conn = psycopg2.connect(host="127.0.0.1", database="devops_school", user="devops", password="devops")

    if conn:
        print ("Connected Successfully")
    else:
        print ("Connection Not Established") 
    cur = conn.cursor()
    if not checkTableExists(conn, 'games') and not checkTableExists(conn, 'players'):
        cur.execute('CREATE TABLE IF NOT EXISTS games (id SERIAL PRIMARY KEY, GAMEDATE DATE  NOT NULL, AWAY_TEAM varchar(32) NOT NULL, HOME_TEAM varchar(32) NOT NULL, SCORES varchar(32))')
        cur.execute('CREATE TABLE IF NOT EXISTS players (id SERIAL PRIMARY KEY, GAMEDATE DATE NOT NULL, NAME varchar(32), TIME_ON_ICE interval)')
        cur.execute('CREATE UNIQUE INDEX idx ON games (GAMEDATE, AWAY_TEAM, HOME_TEAM)')
        cur.execute('CREATE UNIQUE INDEX idy ON players (GAMEDATE, NAME, TIME_ON_ICE)')
    return cur, conn


def insert_data_to_db(all_stlouis_games_list, all_players, cur, conn):
    for line in all_stlouis_games_list:
        sql_string = """ INSERT INTO games (GAMEDATE, AWAY_TEAM, HOME_TEAM, SCORES) VALUES (%s,%s,%s,%s) ON CONFLICT  DO NOTHING"""
        record_to_insert = tuple(line)
        cur.execute(sql_string, record_to_insert)
        conn.commit()
    
    for line in all_players:
        line[2] = change_time_format(line[2])
        sql_string = """ INSERT INTO players (GAMEDATE, NAME, TIME_ON_ICE) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING"""
        record_to_insert = tuple(line)
        cur.execute(sql_string, record_to_insert)
        conn.commit()
    
def get_data_from_db(cur, start_date, end_date):
    cur.execute(f"SELECT TO_CHAR(GAMEDATE, 'YYYY-MM-DD'), AWAY_TEAM, HOME_TEAM, SCORES  FROM games WHERE GAMEDATE BETWEEN '{start_date}' AND '{end_date}'")
    games = list(cur.fetchall())
    cur.execute(f"SELECT TO_CHAR(GAMEDATE, 'YYYY-MM-DD'), NAME, TO_CHAR((TIME_ON_ICE||'second')::interval, 'MI:SS') AS minute_second FROM players WHERE GAMEDATE BETWEEN '{start_date}' AND '{end_date}' ORDER BY TIME_ON_ICE DESC; ")
    players = list(cur.fetchmany(3))
    return games, players
