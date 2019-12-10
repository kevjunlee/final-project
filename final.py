import secrets
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import webbrowser

#Database name and also Json file name for reference
DBNAME = 'artists.db'
FINALJSON = 'final.json'

#API keys for Last.fm web API call
API_KEY = secrets.API_KEY
SHARED_SECRET = secrets.SHARED_SECRET

#caching function
CACHE_FNAME = 'final.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

#make unique combo for web api call
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

#make the actual web api request with caching
def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl, params)
    if unique_ident in CACHE_DICTION:
        print('getting cached data...')
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(baseurl, params)
        data = json.loads(resp.text)
        CACHE_DICTION[unique_ident] = data
        dumped_json_cache = json.dumps(CACHE_DICTION, indent = 4)
        fw = open(CACHE_FNAME,'w')
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

#country class to create instances
class Country():

    def __init__(self, name):
        self.type = type
        self.name = name
    
    def __str__(self):
        return self.name
    
#make the web api call for top artists in any country with the proper ISO 3166-1 name
#this function also adds json information from the api call to the caching file final.json
def get_top_country_artists(country):
    baseurl = 'http://ws.audioscrobbler.com/2.0/?'
    params = {}
    params['method'] = 'geo.gettopartists'
    params['country'] = country
    params['api_key'] = API_KEY
    params['format'] = 'json'
    
    first_search = make_request_using_cache(baseurl, params)

#make the empty SQLite table known as Top Artists in the database artists.db
def make_artist_table():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "DROP TABLE IF EXISTS 'Top Artists';"
    cur.execute(statement)
    
    statement = """
        CREATE TABLE 'Top Artists' (
            'Name' TEXT,
            'Listeners' INTEGER,
            'Mbid' TEXT,
            'Url' TEXT,
            'Country' TEXT);
    """
    cur.execute(statement)
    conn.commit()
    conn.close()

#goes through the cache file final.json and parses through the data for the names of popular artist in that country, number of listeners for the artists, url to artists page, and country that people are searching about
def populate_json():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    with open(FINALJSON) as file:
        json_file = json.load(file)
    artists = json_file
    artists2 = json_file
    random_string_param = list(artists.keys())
    keys  = random_string_param
    for x in keys:
        a1 = artists[x]['topartists']['artist']
        attr = artists[x]['topartists']['@attr']
        origin = attr['country']
        for i in a1:
            insertion = (i['name'], i['listeners'], i['mbid'], i['url'], origin)
            statement = "INSERT INTO 'Top Artists'"
            statement += "VALUES (?,?,?,?,?)"
            cur.execute(statement, insertion)
    conn.commit()
    conn.close()

#goes through Top Artists table in the artist.db database and queries for the top 10 artists for the select country. The query is then put into a dataframe where plotly can graph the data into a bar graph. The x axis shows the names of the artists, y axis shows the number of listeners each artists has, the hover value shows the country that was searched along with the artists listener number and the color distinguishes the popularity for the artists for that specific country
def country_bar_plot(country):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country,))
    data = cur.fetchall()
    rank = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    str(data)
    df = pd.DataFrame([[ij for ij in i] for i in data])
    df.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    df['Rank'] = rank
    print(df)
    df = df.sort_values(['Listeners'], ascending=[1])
    
    graph_data = df
    fig = px.bar(graph_data, x='Name', y='Listeners',
                 hover_data=['Listeners', 'Country'], color='Rank',
                 labels={'Listeners':'Number of Followers for Artist'}, height=400)
    fig.show()

#This function takes five country arguments and calls on them all and adds each country's data to the caching file and Top Artist table in artists.db. It then queries the table to put the arguments into a concatenated dataframe. It then finds the top 5 most frequent artist names in the dataframe and creates a pie chart with hover values showing the frequency of the artists between the 5 countries selected
def compare_countries(country1, country2, country3, country4, country5):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    get_top_country_artists(country1)
    get_top_country_artists(country2)
    get_top_country_artists(country3)
    get_top_country_artists(country4)
    get_top_country_artists(country5)
    
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country1,))
    data1 = cur.fetchall()
    str(data1)
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country2,))
    data2 = cur.fetchall()
    str(data2)
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country3,))
    data3 = cur.fetchall()
    str(data3)
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country4,))
    data4 = cur.fetchall()
    str(data4)
    cur.execute("SELECT Name, Listeners, Country FROM 'Top Artists' WHERE Country = ? LIMIT 10", (country5,))
    data5 = cur.fetchall()
    str(data5)
    
    df1 = pd.DataFrame([[ij for ij in i] for i in data1])
    df1.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    
    df2 = pd.DataFrame([[ij for ij in i] for i in data2])
    df2.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    
    df3 = pd.DataFrame([[ij for ij in i] for i in data3])
    df3.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    
    df4 = pd.DataFrame([[ij for ij in i] for i in data4])
    df4.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    
    df5 = pd.DataFrame([[ij for ij in i] for i in data5])
    df5.rename(columns={0: 'Name', 1: 'Listeners', 2: 'Country'}, inplace=True)
    
    frames = [df1, df2, df3, df4, df5]
    results = pd.concat(frames)
    rdf = pd.DataFrame(results['Name'].value_counts(ascending=False))
    newrdf = rdf[:5]
    fig = go.Figure(data=[go.Pie(labels=newrdf.index, values=newrdf['Name'])])
    fig.show()

#user interface
if __name__ == '__main__':
    command = input('Welcome! Enter a command (or help for options): ')

    while command != 'exit':
        if command.lower() == 'help':
            print(' ')
            print('This is a list of valid commands:                   ')
            print('----------------------------------------------------')
            print('                                                    ')
            print('- topartists <Country>                  ')
            print('description: creates a bar graph for the top 10     ')
            print('             artists in a country')
            print('parameters:  takes in one country name from the ISO ')
            print('             3166-1 list. Except USA not available')
            print('             Ex: topartists Thailand')
            print('                                                    ')
            print('- top5pi                            ')
            print('description: creates a pie chart of the top 5 most  ')
            print('             popular artists for 5 countries        ')
            print('             that are searched')
            print('parameters:  enter 5 different country names from   ')
            print('             the ISO 3166-1 list with spaces        ')
            print('             inbetween.                             ')
            print('             Ex: top5pi Nepal Spain England ...     ')
            print(' ')
            print('- list')
            print('description: opens up ISO 3166-1 list for reference ')
            print('parameters:  none')
            print(' ')
            print('- exit')
            print('description: exits the program')
            print('parameters:  none')
            print(' ')
        elif command[:10].lower() == 'topartists':
            coun = str(command[11:].capitalize())
            get_top_country_artists(coun)
            make_artist_table()
            populate_json()
            country_bar_plot(coun)
        elif command[:6].lower() == 'top5pi':
            coun_l = str(command[7:]).split()
            compare_countries(coun_l[0].capitalize(), coun_l[1].capitalize(), coun_l[2].capitalize(), coun_l[3].capitalize(), coun_l[4].capitalize())
        elif command[:4].lower() == 'list':
            print('Launching ' + 'https://en.wikipedia.org/wiki/ISO_3166-1' + ' for you to learn some more! ')
            webbrowser.open('https://en.wikipedia.org/wiki/ISO_3166-1', new = 2)
        else:
            print('INVALID COMMAND! >:( ')
        command = input('Enter a command (or help for options): ')

    print('Thank you for using the program! Good Bye :) ')

    
