#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import nba_py
import sqlite3
import pandas as pd


def silverK(MOV, elo_diff):
    """Calculate K constant (Source:
    https://www.ergosum.co/nate-silvers-nba-elo-algorithm/).

    Args:
        MOV - Margin of victory.
        elo_diff - ELO difference of teams.
    Returns:
        0, 1 - K constant
    """

    K_0 = 20
    if MOV > 0:
        multiplier = (MOV + 3) ** (0.8) / (7.5 + 0.006 * (elo_diff))
    else:
        multiplier = ( -MOV + 3) ** (0.8) / (7.5 + 0.006 * (-elo_diff))

    return K_0 * multiplier, K_0 * multiplier


def silverS(home_score, away_score):
    """Calculate S for each team (Source:
    https://www.ergosum.co/nate-silvers-nba-elo-algorithm/).

    Args:
        home_score - score of home team.
        away_score - score of away team.
    Returns:
        0: - S for the home team.
        1: - S for the away team.
    """

    S_home, S_away = 0, 0
    if home_score > away_score:
        S_home = 1
    elif away_score > home_score:
        S_away = 1
    else:
        S_home, S_away = .5, .5

    return S_home, S_away


def elo_prediction(home_rating, away_rating):
    """Calculate the expected win probability of the home team (Source:
    https://www.ergosum.co/nate-silvers-nba-elo-algorithm/).

    Args:
        home_rating - initial home elo score.
        away_rating - initial away elo score.
    Returns:
        E_home - expected win probability of the home team.
    """

    E_home = 1. / (1 + 10 ** ((away_rating - home_rating) / (400.)))

    return E_home


def silver_elo_update(home_score, away_score, home_rating, away_rating):
    """Calculate change in elo for home and away teams Source:
    https://www.ergosum.co/nate-silvers-nba-elo-algorithm/).

    Args:
        home_score: score of home team.
        away_score: score of away team.
        home_rating: initial home elo score.
        away_rating: initial away elo score.
    Returns:
        0: change in home elo.
        1: change in away elo.
    """

    HOME_AD = 100.
    home_rating += HOME_AD
    E_home = elo_prediction(home_rating, away_rating)
    E_away = 1 - E_home
    elo_diff = home_rating - away_rating
    MOV = home_score - away_score

    S_home,S_away = silverS(home_score,away_score)
    if S_home>0:
        K_home,K_away =  silverK(MOV,elo_diff)
    else:
        K_home,K_away =  silverK(MOV,elo_diff)

    return K_home * (S_home - E_home), K_away * (S_away - E_away)


def init_db(data=os.path.join("../", "data", "external", "nbaallelo.csv"),
            db=os.path.join("..", "data", "outputs", "NBA_ELO.db")):
    """Recreate db from original 538 data.
    Args:
        data - path to 538 csv.
        db - path to resulting db.
    """

    # -- Read 538 ELO data.
    cols0 = ["game_id", "date_game", "team_id", "pts", "elo_i", "elo_n"]
    df = pd.read_csv(data, usecols=cols0)
    df.date_game = pd.to_datetime(df.date_game)

    # -- Reformat (1 game, 1 row), and write to db.
    away, home = df[df.index % 2 == 0], df[df.index % 2 == 1]
    with sqlite3.connect(db) as conn:
        away.merge(home, on=["game_id", "date_game"],
                   suffixes=("_away", "_home")) \
            .drop("game_id", axis=1) \
            .replace({"team_id_away": {"BKN": u"BRK", "PHX": u"PHO"},
                      "team_id_home": {"BKN": u"BRK", "PHX": u"PHO"}}) \
            .to_sql("nba_elo", conn, if_exists="replace")


def read_db(db=os.path.join("..", "data", "outputs", "NBA_ELO.db")):
    """Read data from db.
    Args:
        db - path to db.
    Returns:
        Pandas dataframe of nba_elo table.
    """

    # -- Load data from db.
    with sqlite3.connect(db) as conn:
        return pd.read_sql("SELECT * FROM nba_elo", conn,
                           index_col="index", parse_dates=["date_game"])


def get_games(db=os.path.join("..", "data", "outputs", "NBA_ELO.db")):
    """Using nba_py get data for all games that are not in the DB.
    NOTE: seasons variable must be updated for future seasons (this is dumb).

    Returns:
        new_games - pandas dataframe of all new games.
    """

    # -- Exclude pre-season.
    seasons = pd.concat([pd.date_range("2015-10-27", "2016-06-02").to_series(),
                         pd.date_range("2016-10-25", "2017-06-01").to_series(),
                         pd.date_range("2017-10-17", "2018-06-17").to_series()])

    # -- Load data from db.
    df = read_db(db)

    new_games = pd.DataFrame() # Empty df to append new game data.
    cols1 = ["GAME_ID", "GAME_DATE_EST", "TEAM_ABBREVIATION", "PTS"]

    # -- For each day since last game, check for game data.
    for day in pd.date_range(df.date_game.max(), pd.datetime.today()):
        if day in seasons:
            print("Collecting data for games on: {}".format(day.date()), end="\r")
            sys.stdout.flush()
            try:
                sb = nba_py.Scoreboard(day.month, day.day, day.year)
                days_games = sb.line_score()[cols1]
                if len(days_games) > 0 :
                    away = days_games[days_games.index % 2 == 0]
                    home = days_games[days_games.index % 2 == 1]
                    days_games = away.merge(home,
                                            on=["GAME_DATE_EST", "GAME_ID"],
                                            suffixes=("_AWAY", "_HOME")) \
                                     .drop("GAME_ID", axis=1)
                    new_games = pd.concat([new_games, days_games])
            except:
                print("Error at {}. Rerun, to continue from here.".format(day))
                break

    return new_games


def update_db(new_games,
              db=os.path.join("..", "data", "outputs", "NBA_ELO.db")):
    """Puts new games into db.
    Args:
        new_games - pandas dataframe containing new game info.
        db - path to db.
    """

    cols = {"GAME_DATE_EST": "date_game", "TEAM_ABBREVIATION_AWAY": "team_id_away",
            "PTS_AWAY": "pts_away", "TEAM_ABBREVIATION_HOME": "team_id_home",
            "PTS_HOME": "pts_home"}

    with sqlite3.connect(db) as conn:
        tmp = pd.concat([read_db(db), new_games.rename(columns=cols)]) \
                .reset_index(drop=True) \
                .replace({"team_id_away": {"BKN": u"BRK", "PHX": u"PHO"},
                          "team_id_home": {"BKN": u"BRK", "PHX": u"PHO"}})
        tmp.date_game = tmp.date_game.astype(str)
        tmp.to_sql("nba_elo", conn, if_exists="replace")


def last_elo(df):
    """Calculate the last ELO for each team (past 2016).
    Args:
        df - pandas dataframe containing database table.
    Returns:
        last_elo (dict) - dictionary where tm: elo score.
        max_date - last date in table.
    """

    last_elo = {}
    max_date = pd.datetime(2014, 1, 1)
    for tm in df[df.date_game > pd.datetime(2016, 1, 1)].team_id_away.unique():
        try:
            # -- Subset table to get most recent record with an ELO rating.
            tmp = df[((~df.elo_i_home.isnull()) & (df.team_id_away == tm)) |
                     ((~df.elo_i_home.isnull()) & (df.team_id_home == tm))] \
                    .sort_values("date_game").iloc[-1]
            max_date = max(max_date, tmp.date_game)
        except:
            print("Error with: {}".format(tm))
        # -- Store ELO in dictionary.
        if tmp.team_id_home == tm:
            last_elo[tm] = tmp.elo_n_home
        else:
            last_elo[tm] = tmp.elo_n_away

    return last_elo, max_date


def new_season(elo_dict):
    """Update ELO score when rolling over into a new season.
    Args:
        elo_dict - last ELO scores for each team.
    Return:
        elo_dict - updated ELO scores.
    """

    for tm in elo_dict.keys():
        elo_dict[tm] = elo_dict[tm] * 0.75 + 1505 * 0.25

    return elo_dict


def update_elo(df, db=os.path.join("..", "data", "outputs", "NBA_ELO.db"),
               in_season=False):
    """Update ELO score for new records in nba_elo table and write to db.
    Args:
        df - pandas dataframe of nba_elo.
        elo - last ELO scores for each team.
        in_season - Do the ELO scores need to be rolled over between seasons?
    """

    seasons = [pd.date_range("2015-10-27", "2016-06-02").to_series(),
               pd.date_range("2016-10-25", "2017-06-01").to_series(),
               pd.date_range("2017-10-17", "2018-06-17").to_series()]

    df = df.copy()
    elo, max_date = last_elo(df)
    for season in seasons:
        if not in_season:
            elo = new_season(elo)
        try:
            for idx, row in df[df.date_game.isin(season)].iterrows():
                if sum(row.isnull()) > 0:
                    home_tm, away_tm = row.team_id_home, row.team_id_away
                    h_elo_i, a_elo_i = elo[home_tm], elo[away_tm]
                    h_delta, a_delta = silver_elo_update(row.pts_home, row.pts_away, h_elo_i, a_elo_i)
                    elo[home_tm] = h_elo_i + h_delta
                    elo[away_tm] = a_elo_i + a_delta

                    df.set_value(idx, "elo_i_away", a_elo_i)
                    df.set_value(idx, "elo_i_home", h_elo_i)

                    df.set_value(idx, "elo_n_away", elo[away_tm])
                    df.set_value(idx, "elo_n_home", elo[home_tm])
        except:
            pass
    print(df)
    with sqlite3.connect(db) as conn:
        df.to_sql("nba_elo", conn, if_exists="replace")
