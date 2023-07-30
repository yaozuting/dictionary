from deta import Deta
import os
from dotenv import load_dotenv

load_dotenv()
Deta_Key = os.getenv("Deta_Key")

#initialize with a project key
deta = Deta(Deta_Key)

#create/ connect to a database
db = deta.Base('dictionary')

def insert_word(word,translation,audio,meaning,example_sentences,):
    return db.put({"key":word,"Translation":translation,"audio":audio,"Meanings":meaning,"sentences":example_sentences})

def fetch_all_words():
    all = db.fetch()
    return all.items

def delete_word(word):
    return db.delete(word)

#use the word as key to get all the associate informations
def get_word(word):
    return db.get(word)