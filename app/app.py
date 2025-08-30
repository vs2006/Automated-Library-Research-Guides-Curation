import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from pprint import pprint
#from tqdm import tqdm
from flask import Flask, render_template, request
import json



app = Flask(__name__)





def check_access(title: str, year: int):
    df = pd.read_excel("library_titles.xlsx")
    title = title.lower()
    year= int(year)
    
    if (title not in df["title"].values):
        return False
    
    details = df.loc[ df["title"] == title ] 
    from_year = details.iloc[0]["from"]
    to_year = details.iloc[0]["to"]
    
    if ( (pd.notna(from_year)) and (pd.isna(to_year)) ):
        if (year >= from_year):
            return True
        return False
    
    if ( (pd.notna(from_year)) and (pd.notna(to_year)) ):
        if ((year <= to_year) and (year >= from_year)):
            return True
        return False
    
    if( (pd.isna(from_year)) and (pd.notna(to_year)) ):
        if (year <= to_year):
            return True
        return False
    
    return True

    




def get_sub_articles(topic: str):
    articles = list()
    url = r'https://api.openalex.org/works?filter=type:article,open_access.is_oa:false&per-page=50'
    url =url + r'&search=' + topic
    url1 = url + r'&cursor=*'
    #pbar = tqdm(desc="Fetching pages", unit="page")
    i = 1
    
    while True: 
        response = requests.get(url=url1)
        data = response.json()
        results= data["results"]
        #print(json.dumps(results, indent=2))
        
        for ele in results:
            title = ele["title"]
            year = ele.get("publication_year")
            
            source = ele.get("primary_location", {})
            
            if (source is not None):
                source = source.get("source")
                if (source is not None):
                    source = source.get("display_name")
                    
            if (source is None):
                continue
            
            if ((year is None) or (source is None)):
                continue
            
            if (check_access(source, year)):
                    location = ele.get("primary_location", {}).get("landing_page_url")
                    
                    if (location is None):
                        location = ele.get("ids", {}).get("openalex")
                    articles.append([ title , location ])
            else:
                continue
        
        if (data.get("meta",{}).get("next_cursor") is None):
            break
        
        cursor = data.get("meta",{}).get("next_cursor")
        url1 = url + r'&cursor=' + cursor
        
        i+=1
        #pbar.update(1)
        
        if (i>1):
            break
    
    return articles





def get_oa_articles(topic: str):
    articles = list()
    url = r'https://api.openalex.org/works?filter=type:article,open_access.is_oa:true&per-page=50'
    url =url + r'&search=' + topic
    url1 = url + r'&cursor=*'
    #pbar = tqdm(desc="Fetching pages", unit="page")
    i = 1
    
    while True: 
        response = requests.get(url=url1)
        data = response.json()
        results= data["results"]
        
        for ele in results:
            title = ele["title"]
            location = ele.get("best_oa_location", {})
            
            if (location is not None):
                location = location.get("landing_page_url")
                
            if (location is None):
                location = ele.get("ids", {}).get("openalex")
            
            articles.append([ title , location ])
        
        if (data.get("meta",{}).get("next_cursor") is None):
            break
        
        cursor = data.get("meta",{}).get("next_cursor")
        url1 = url + r'&cursor=' + cursor
        
        i+=1
        #pbar.update(1)
        
        if (i>1):
            break
    
    return articles


def get_articles(topic: str):
    result = list()
    
    result.extend(get_oa_articles(topic))
    result.extend(get_sub_articles(topic))
    
    return result



#===================================================================================================================



# Get all ISBNs in the library
def get_koha_isbns():

    koha_url = "http://localhost:8000/api/v1"
    username = "circulation"
    password = "circulation"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/marc"
    }
    response = requests.get(
        f"{koha_url}/biblios?_per_page=1000000", #Replace per_page count with a number more than the total number of books present in the library
        auth=HTTPBasicAuth(username, password),
        headers=headers
    )
    
    biblios = response.json()
    result = dict()
    url1: str = r'https://koha.ashoka.edu.in/cgi-bin/koha/opac-detail.pl?biblionumber='

    for biblio in biblios:
        for field in biblio.get("fields", {}):
            subfields = field.get("020", {}).get("subfields", {})
            for subfield in subfields:
                if "a" in subfield:
                    result[(subfield["a"].split()[0])] = [ str(biblio.get("title")) , (url1 + str(biblio.get("biblio_id"))) ]
    
    with open("data.json", "w") as f:
        json.dump(result, f, indent=4)

    return None


#Get ISBNs from Google Books
def get_google_books_isbns(topic):

    url = f"https://www.googleapis.com/books/v1/volumes?q={topic}"
    response = requests.get(url)
    
    items = response.json().get("items", [])
    
    isbns = []
    for item in items:
        identifiers = item.get("volumeInfo", {}).get("industryIdentifiers", [])
        for id_info in identifiers:
            if "ISBN" in id_info.get("type", ""):
                isbns.append(id_info.get("identifier", ""))
    return list(set(isbns))


def get_books(topic):
    
    google_isbns = get_google_books_isbns(topic)

    google_isbns_set = set(google_isbns)

    with open("data.json", "r") as f:
        loaded = json.load(f)

    found_isbns = []

    for isbn in google_isbns_set:
        if isbn in loaded:
            found_isbns.append(loaded[isbn])

    return found_isbns






#===================================================================================================================





@app.route("/")
def get_topic():
    return render_template("index.html")


@app.route("/articles")
def display_articles():
    if "topic" in request.args:
        topic: str = request.args["topic"]
    else:
        return "Invalid input"
    
    return render_template("articles.html", articles=get_articles(topic))


@app.route("/books")
def display_books():
    if "topic" in request.args:
        topic: str = request.args["topic"]
    else:
        return "Invalid input"
    
    return render_template("books.html", books=get_books(topic))