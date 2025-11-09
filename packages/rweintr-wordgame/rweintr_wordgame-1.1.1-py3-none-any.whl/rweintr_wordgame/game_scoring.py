from sqlalchemy import create_engine,func,desc,asc
from sqlalchemy.orm import sessionmaker
from rweintr_wordgame.game_models import Player, Game
from datetime import datetime
from importlib import resources
from rweintr_wordgame import NUMBER_OF_GUESSES_EASY,NUMBER_OF_GUESSES_MEDIUM,NUMBER_OF_GUESSES_DIFFICULT
from rweintr_wordgame import EASY_LEVEL_MULTIPLIER,MEDIUM_LEVEL_MULTIPLIER,DIFFICULT_LEVEL_MULTIPLIER

def create_session():
    engine = create_engine("sqlite:///./src/rweintr_wordgame/data/wgplayers.db", echo=False)
    Session = sessionmaker(engine)
    return Session()

def get_scores_by_alias(session,alias,sort_col_name="score",limit_value=5):
    '''  n highest (default) or most recent scores for a player '''
    return (
        session.query(Player.alias,Game.play_dt,Game.score) 
        .join(Game)
        .where(Player.alias==alias) 
        .order_by(desc(getattr(Game,sort_col_name)),desc(Game.play_dt))
        .limit(limit_value)
        .all() 
    )

def get_max_score(session,alias):
    ''' get high score for player '''
    return (
        session.query(Player.alias,func.max(Game.score).label("high_score"))
        .join(Game)
        .where(Player.alias==alias)
        .one()
    )

def rank_games_played(session,limit_value=10):
    ''' rank top n players with most games played'''
    return (
        session.query(Player.alias, 
        func.count(Game.score).label("total_games")) 
        .join(Game) 
        .group_by(Player.alias) 
        .order_by(func.count(Game.score).desc(),Player.alias) 
        .limit(limit_value)
        .all()
    )

def rank_by_wins(session,limit_value=10):
    ''' rank top n winners '''
    query1 = (session.query(Player.alias, 
    func.count(Game.score).label("wins"))
    .join(Game)
    .where(Game.score > 0) 
    .group_by(Player.alias))

    query2 = (session.query(Player.alias,
    func.sum(Game.score).label("wins"))
    .join(Game)
    .group_by(Player.alias)
    .having(func.sum(Game.score)==0))
    
    query3 = query1.union_all(query2)
    return(
        query3.order_by(desc("wins"),Player.alias).limit(limit_value).all()
    )

def rank_by_avg_score(session,limit_value=3,descending=True):
    ''' rank top n players by average score '''
    direction = desc if descending else asc
    return (
        session.query(Player.alias, 
        (func.sum(Game.score)/func.count(Game.score)).label("average_score")) 
        .join(Game) 
        .group_by(Player.alias) 
        .order_by(direction("average_score"),asc(Player.alias)) 
        .limit(limit_value)
        .all()
    )

def add_player(session,alias):
    ''' add a new player if does not exist '''
    #check if player exists
    player = (
        session.query(Player)
        .filter(Player.alias==alias)
        .one_or_none()
    )
    if player is not None:
        return player
    #player does not exist - add player
    now=datetime.now()
    player = Player(alias=alias,start_dt=now.strftime("%Y-%m-%d %H:%M:%S"))
    session.add(player)
    return player

def add_game(session,alias,score):
    ''' add game result for player '''
    #add player if nec.
    player=add_player(session,alias)
    #add game score for player
    now=datetime.now()
    game = Game(score=score,play_dt=now.strftime("%Y-%m-%d %H:%M:%S"))
    game.player=player
    session.add(game)
    session.commit()
    return

def calculate_score(guesses,level):
    ''' calculate score - fewer guesses and higher difficulty 
        level yield higher scores '''
    if level == str(1):
        num_guesses_left = NUMBER_OF_GUESSES_EASY - guesses + 1
        score = num_guesses_left * 10 * EASY_LEVEL_MULTIPLIER
    elif level == str(2):
        num_guesses_left = NUMBER_OF_GUESSES_MEDIUM - guesses + 1
        score = num_guesses_left * 10 * MEDIUM_LEVEL_MULTIPLIER
    else:
        num_guesses_left = NUMBER_OF_GUESSES_DIFFICULT - guesses + 1
        score = num_guesses_left * 10 * DIFFICULT_LEVEL_MULTIPLIER
    return score

def show_stats(session,alias):
    ''' display statistics for player '''
    scores=get_scores_by_alias(session,alias)
    print(f"\n5 Highest Scores for \033[1m{alias}\033[0m")
    for row in scores:
        print(f"{row.score} on {row.play_dt}")
    averages=rank_by_avg_score(session)
    print("\nTop 3 Player Scoring Averages")
    for row in averages:
        if row.alias == alias:
            print(f"\033[1m{row.alias}\033[0m  {round(row.average_score)}")
        else:
            print(f"{row.alias}  {round(row.average_score)}")
    
    games_played = rank_games_played(session)
    wins = rank_by_wins(session,3)
    print("\nTop 3 Winners With Winning Percentages")
    for row_wins in wins:
        for row_games in games_played:
            if row_games.alias == row_wins.alias:
                if row_games.alias == alias:
                    print(f"Player: \033[1m{row_wins.alias}\033[0m, Wins: {row_wins.wins} Games: {row_games.total_games} Pctg: {round((row_wins.wins/row_games.total_games)*100)}%")
                else:
                    print(f"Player: {row_wins.alias}, Wins: {row_wins.wins} Games: {row_games.total_games} Pctg: {round((row_wins.wins/row_games.total_games)*100)}%")
    return