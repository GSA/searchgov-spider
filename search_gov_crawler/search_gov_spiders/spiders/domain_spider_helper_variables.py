import os
import sys

PLAYWRIGHT_FLAG = True


# fmt: off
filter_extensions = [
    "cfm","css","eventsource","exe","fetch","font","gif",
    "ibooks","ics","image","jpeg","jpg","js","manifest",
    "media","mp3","mp4","nc","png","ppt","pptx",
    "prj","rss","sfx","stylesheet","svg","tar.gz","tar",
    "tif","wav","websocket","wmv","xhr","xml","zip",]
# fmt: on

starting_urls = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "../utility_files/startingUrls.txt"
)

start_urls_list = []
with open(starting_urls, encoding="utf-8") as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "../utility_files/domains.txt"
)

domains_list = []
with open(domains, encoding="utf-8") as file:
    while line := file.readline():
        domains_list.append(line.rstrip())
