import os.path

BOT_TOKEN = ""  # From @BotFather
API_ID = 0  # from my.telegram.org
API_HASH = ""  # from my.telegram.org

BUTTONS_PER_ROW = 2  # how many rows per button to display
# PATH of the json file to store the data
JSON_PATH = os.path.join(os.path.dirname(__file__), "data.json")
if not os.path.isfile(JSON_PATH):
    with open(JSON_PATH, "w") as f:
        f.write("{}")
