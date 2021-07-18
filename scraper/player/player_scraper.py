from scraper.scrape_functions import get_historicals_by_gw
from scraper.scraper_constants import seasons, team_tables, path
import numpy as np
import os

gameweeklist = list(np.arange(1, 39))
ffs_tables = [f'{x}_' + str(season) for season in seasons for x in team_tables]
ffs_df_dict = {}
for season in seasons:
    for feature in team_tables:
        df = get_historicals_by_gw(str(season), gameweeklist, feature)
        ffs_df_dict[f"{feature}_{season}"] = df
        print(f"Scraped {feature, season}")

for table in ffs_tables:
    output_file_path = os.path.join(path, f"{table}")
    ffs_df_dict[table].to_csv(output_file_path)
