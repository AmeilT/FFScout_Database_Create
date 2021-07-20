import os
from pathlib import Path

seasons=[2011,2012,2013,2014,2015,2016,2017,2018,2019,2020]
tables = ["involvement", "distribution", "goal-threat", "defending", "set-pieces", "kpi-attacking", "kpi-defending"]
cwd=Path(os.getcwd())
datafilepath=rf"{str(cwd.parent.absolute())}/scraper/data/player data"

