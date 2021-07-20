# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())

import numpy as np
import os

from scraper.scrape_functions import create_team_table_gw
from scraper.scraper_constants import seasons, team_tables, stored_path

gameweeklist = list(np.arange(1, 39))
ffs_tables = [f'{x}_' + str(season) for season in seasons for x in team_tables]
ffs_df_dict = {}
for season in seasons:
    for feature in team_tables:
        df = create_team_table_gw(str(season), gameweeklist, feature)
        ffs_df_dict[f"teams_{feature}_{season}"] = df
        print(f"Scraped {feature, season}")

for table in ffs_tables:
    output_file_path = os.path.join(stored_path, f"{table}")
    ffs_df_dict[table].to_csv(output_file_path)
