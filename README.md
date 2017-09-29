<h1 align="center">
  NBA ELO
</h1>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v2.7-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview
This projects aims to provide up-to-date ELO scores by extending [data](https://github.com/fivethirtyeight/data/tree/master/nba-elo) from 538. Both NBA_ELO.db and nba_elo.csv contain ELO scores up to the conclusion of the 2016-17 season. The resulting table looks like:

| index | date_game | elo_i_away | elo_i_home | elo_n_away | elo_n_home | pts_away | pts_home | team_id_away | team_id_home |
|-------|------------|------------|------------|------------|------------|----------|----------|--------------|--------------|
| 0 | 1946-11-01 | 1300.0 | 1300.0 | 1293.2767 | 1306.7233 | 66 | 68 | TRH | NYK |

## Requirements
```
nba_py
```

## Project Organization
```
├── README.md
├── LICENSE.txt
├── .gitignore
├── NBA_ELO
│   └──  NBA_ELO.py  
├── notebooks
│   └──  0.0-JV-ELOComparison.ipynb
└── data
    ├── external
    │   └── nbaallelo.csv
    └── output  
        ├── NBA_ELO.db  (table name: nba_elo)
        └── nba_elo.csv
```

## Credit
This project uses functions from [rogerfitz/tutorials/Nate Silver ELO.](https://github.com/rogerfitz/tutorials/tree/master/Nate%20Silver%20ELO)
