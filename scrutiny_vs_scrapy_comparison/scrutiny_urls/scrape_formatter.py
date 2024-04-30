import csv
import pandas as pd
import os

# to run, enter at the prompt: `python3.9 scrape_formatter.py`

# assign directory
directory = "raw"
 
# iterate over files in that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        try:
            # read the file into a Pandas DataFrame
            df = pd.read_csv(f)

            # isolate rows that have 200 status
            good_urls = df.loc[df['status'].eq("200 no error")]

            # dedup lines
            deduped = good_urls.drop_duplicates(subset=["url"], keep="first", inplace=False, ignore_index=False)

            # write text file with only URLs from those rows
            deduped['url'].to_csv('processed/' + filename.replace(".csv", "") + ".txt", index=False, header=False)
            
            # print message
            print(filename + " is finished processing.")

        except Exception as e:
            print("Could not proccess " + filename + ". Error: " + str(e))
            
# when complete, cd into /processed/ run `cat *.txt >> aggregated` from the command line
# then run `gsplit -b 3500K aggregated aggregated- --additional-suffix=".txt"`