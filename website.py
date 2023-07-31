from PyDictionary import PyDictionary
from bs4 import BeautifulSoup
import requests
import streamlit as st
from streamlit_option_menu import option_menu
from translate import Translator
import database as db #local import
import nltk
nltk.download('punkt')
from nltk import word_tokenize

dictionary = PyDictionary()

def get_sound(word):
    output = None
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        data = response.json()
        entry = data[0]
        phonetics = entry['phonetics']
        texts, audios = [], []
        for phonetic in phonetics:
            # text = phonetic['text']
            audio = phonetic['audio'] if phonetic['audio'] != ' ' else ''
            # texts.append(text)
            if audio != '':
               audios.append(audio)
        output = {"Audios": audios[0]}
    except (IndexError,KeyError):
        output = "wrong"
    return output

def get_all_words():
    all_items = db.fetch_all_words()
    words = [item['key'] for item in all_items]
    return words

def get_meanings(word):
    meaning = dictionary.meaning(word)
    return meaning

def word_count(text):
    words = word_tokenize(text)
    return len(words)

def get_example_sentences(word):
    url = f"https://www.yourdictionary.com/{word}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    sentences = []
    divs = soup.find_all("div", class_="sentence component")
    for div in divs:
        try:
            text = div.text.strip()
            sentences.append(text)
        except AttributeError:
            pass
    return sentences


from gingerit.gingerit import *

def sentence_corrector(sentence,count):
    # Initialize GingerIt
    ginger = GingerIt()
    try:
    # Correct the sentence
     result = ginger.parse(sentence)
     corrected_sentence = result['result']
    except KeyError: return f"Try to make it under 120 words currently at {count}!!"
    return f"{corrected_sentence}    ({count}words)"

#creating a website
page_title = "Dictionary "
page_icon = "📚"
# Custom theme colors

#website configuration
st.set_page_config(page_title = page_title,page_icon=page_icon,layout = "centered")

#hide streamlit style
hide_st_style = """
                 <style>
                 #MainMenu{visibility:hidden;}
                 footer{visibility:hidden;}
                 header{visibility:hidden;}
                 </style>
                 """
st.markdown(hide_st_style,unsafe_allow_html=True)

selected = option_menu(
            menu_title = "Main Menu",
            options = ['Dictionary',"History","Sentence Corrector"],
            icons = ['📖','🖥','🖋'],
            default_index = 0,
            orientation = "horizontal",
            styles={
    "container": {"padding": "0!important", "background-color": "#E6E6FA"},
    "icon": {"color": "orange", "font-size": "25px"}, 
    "nav-link": {"font-size": "20px", "text-align": "center", "margin":"0px", "--hover-color": "#98FB98"},
    "nav-link-selected": {"background-color": "peach"},
}
    )

#dictionary
if selected == "Dictionary":
#----header section--
 st.header('Dictionary')

 with st.form(key="dictionary_form"):
    search_word = st.text_input("Input a word")
    submitted = st.form_submit_button('Send')

 if submitted:
#   st.write(f"Searching for {search_word}......")
    meaning = get_meanings(search_word)
    example_sentences = get_example_sentences(search_word)
    audio = get_sound(search_word)
    audio_url = list(get_sound(search_word).values())[0] if audio != "wrong" else None

    translator= Translator(to_lang="zh")
    translation = translator.translate(search_word)

    biggest = "28px"
    big = "24px"
    small = "16px"
    fathest = "60px"
    far = "40px"
    close = "20px"

    if meaning:
        db.insert_word(search_word.capitalize(),translation,audio_url,meaning,example_sentences)
        st.header(f'{search_word.capitalize()}    ({translation})')
        st.audio(audio_url)
        st.markdown(f"<p style = 'font-size:{biggest};margin-left:{close};'>Meanings:</p>",unsafe_allow_html=True)
        for types,explanation in meaning.items():
            st.markdown(f"<p style='font-size: {big};margin-bottom:0;margin-left: {far};'>{types}</p>",unsafe_allow_html=True)
            for explane in explanation:
                st.markdown(f"<p style='font-size: {small}; margin-left: {fathest}; margin-top: 0; margin-bottom: 0;'>- {explane}</p>", unsafe_allow_html=True)
        st.write("##")
        st.markdown(f"<p style = 'font-size:{biggest};margin-left:{close};'>Example Sentences:</p>",unsafe_allow_html = True)
        for sentence in example_sentences:
            st.markdown(f"<p style='font-size: {small}; margin-left:{far}; margin-top: 0; margin-bottom: 0;'>- {sentence}</p>", unsafe_allow_html=True)
        
    else:
        st.write("##")
        st.write("You might need to double check your spelling")

#sentence corrector
if selected =="Sentence Corrector":
 with st.container():    
    st.header("Sentence Corrector")
    input_sentence = st.text_area("Input a sentence:")
    count = word_count(input_sentence)
    submit = st.button('Click me')

    if submit :
        result = sentence_corrector(input_sentence,count)
        st.text_area("Result:", value=result, height=200, key="result_box")

#history
if selected =="History":
    st.header("History")
    words = get_all_words()
    for w in words:
        word = db.get_word(w)
        with st.expander(w):
            st.write(word['Translation'])
            st.audio(word['audio'])
            st.write("Meanings")
            st.write(word['Meanings'])
            st.write('Example Sentences')
            st.write(word['sentences'])
            delete = st.button("Delete")
            if delete: db.delete_word(w,key=f'Delete_{w}')
