import json
import random
from pathlib import Path
from typing import Iterator

import requests
from bs4 import BeautifulSoup

TOPICS_URL = "https://blog.kialo-edu.com/debate-ideas/philosophical-debate-topics/"
TOPICS_FILENAME = "debate_list.json"


def get_topics() -> Iterator[str]:
    data = requests.get(TOPICS_URL)
    soup = BeautifulSoup(data.content, "html.parser")
    for x in soup.find_all("li"):
        if x.text.startswith("\n"):
            break
        yield x.text


# Function gives you a question from a list of topics by a blog
def get_prompt() -> str:
    path = Path("../"+TOPICS_FILENAME)
    if path.exists():
        data = json.loads(path.read_text())
    else:
        topics = list(get_topics())
        with open(TOPICS_FILENAME, "w") as f:
            json.dump(topics, f)
        data = topics
    return random.choice(data)


if __name__ == "__main__":
    get_prompt()
