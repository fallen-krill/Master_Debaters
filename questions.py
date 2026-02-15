import requests
import random, string
from bs4 import BeautifulSoup
# Function gives you a question from a list of topics by a blog
def getPrompt():
    def getTopics():
        data = requests.get('https://blog.kialo-edu.com/debate-ideas/philosophical-debate-topics/')
        s = BeautifulSoup(data.content, 'html.parser')
        listOfTopics = []
        f = open("debate_list.txt", "w+")
        for x in s.find_all('li'):
            if x.getText().find("\n")==0:
                break
            f.write(x.getText()+"\n")
        f.close()

    try:
        f = open("debate_list.txt", "r")
    except FileNotFoundError:
        getTopics()
        f = open("debate_list.txt", "r")
    data = f.readlines()
    f.close()
    return (data[random.randint(0, len(data)-1)])

getPrompt()
username = "".join(random.choices(string.ascii_lowercase, k=10))
print(username)