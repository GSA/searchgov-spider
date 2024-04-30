import csv
import difflib
import urllib.parse
import re

def csv_to_set(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        url_list = list(reader)
        url_list = list(map(''.join, url_list))
    f.close()
    url_set = set(url_list)
    return url_set

def txt_to_set(file_path):
    with open(file_path, 'r') as f:
       url_list = f.readlines()
       url_list = list(map(''.join, url_list))
    f.close()
    fixed_urls = []
    for url in url_list:
        fixed_urls.append(re.sub("\n", "", url))
    url_set = set(fixed_urls)
    return url_set


def make_comparisons(scrapy_urls, scrutiny_urls):
    urls_missing_in_scrapy_urls = scrutiny_urls - scrapy_urls

    # Find the urls that are in group 2 but missing in group 1
    urls_missing_in_scrutiny_urls = scrapy_urls - scrutiny_urls

    # Find the urls that are in both groups
    urls_in_common = scrutiny_urls & scrapy_urls

    return (urls_missing_in_scrapy_urls, urls_missing_in_scrutiny_urls, urls_in_common)
    
  