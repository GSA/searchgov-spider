import plistlib

# Search.gov uses Scrutiny, which stores its config as a plist.
# We want to pull the startingUrl value from the file for each crawl.

# To run, enter at the prompt: 'python3 scrutiny_plist_parse.py'

# Assign the file path to the Scrutiny plist
plist_file_path = "scrutiny.plist"
# Assign the file path to the desired text file for the URLs to be stored
txt_file_path = "startingUrls.txt"


# Parses plist for startingURLs
def parse_plist_file(file_path):
    with open(file_path, "rb") as file:
        plist_data = plistlib.load(file)
        # Checks if the plist is formatted as an array ("list" in python)
        if isinstance(plist_data, list):
            starting_urls = []
            # Iterates through the items in the plist array
            for item in plist_data:
                # Checks that the item is a dictionary
                if isinstance(item, dict):
                    # Retrieve the startingURL
                    url = item.get("startingUrl")
                    # Checks that the URL exists and then adds it to the starting_urls list
                    if url:
                        starting_urls.append(url)
            return starting_urls
        else:
            raise ValueError("Invalid plist format")


# Write the starting_urls list to the txt file assigned above
def write_urls_to_file(file_path, urls):
    with open(file_path, "w") as file:
        for url in urls:
            file.write(url + "\n")


# Executing the two functions
starting_urls = parse_plist_file(plist_file_path)
write_urls_to_file(txt_file_path, starting_urls)
