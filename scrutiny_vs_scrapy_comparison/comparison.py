import csv
import difflib
import urllib.parse
import re
from comparison_functions import *
import pandas as pd

# to run, enter at the prompt: `python3 comparison.py`

scrapy_urls_folder = '/scrapy_urls'
scrutiny_urls_folder = '/scrutiny_urls/processed'

scrapy_paths = [scrapy_urls_folder + '/armymwr_urls.csv',
                scrapy_urls_folder + '/james_webb_urls.csv',
                scrapy_urls_folder + '/travel_dod_mil_urls.csv',
                scrapy_urls_folder + '/veteran_affair_urls.csv']
scrutiny_paths = [scrutiny_urls_folder + '/armymwr.txt',
                  scrutiny_urls_folder + '/james_webb.txt',
                  scrutiny_urls_folder + '/travel_dod_mil.txt',
                  scrutiny_urls_folder + '/veteran_affairs.txt']
text_gaps = ['armymwr',
             'james webb',
             'travel.dod.mil',
             'veteran_affairs'
             ]

for i in range(0, len(scrapy_paths)):
    scrapy_urls = csv_to_set(scrapy_paths[i])
    scrutiny_urls = txt_to_set(scrutiny_paths[i])
    url_sets = make_comparisons(scrapy_urls, scrutiny_urls)
    with open('processed/' + str(text_gaps[i]) + '.csv', 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(pd.Series(list(url_sets[0])))
        writer.writerow(pd.Series(list(url_sets[1])))
        writer.writerow(pd.Series(list(url_sets[2])))
    csvfile.close()







