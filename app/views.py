from app import app

import requests,os,json
import pandas as pd
from flask import render_template,request,redirect,url_for
from bs4 import BeautifulSoup
from app.config import headers
from app import utils

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/extract")
def display_form():
    return render_template('extract.html')

@app.route("/extract", methods=["POST"])
def extract(): 
    product_id = request.form.get('product_id')
    next_page=f"https://www.ceneo.pl/{product_id}#tab=reviews"
    response = requests.get(next_page, headers=headers)
    if response.status_code ==200:
        page_dom = BeautifulSoup(response.text,"html.parser")
        product_name = utils.extract_feature(page_dom,"h1.product-top__product-info__name")
        opinions_count = utils.extract_feature(page_dom,"a.product-review__link > span")
        if not opinions_count:
            error="Dla produktu o podanym id nie ma jeszcze żadnych opinii"
            return render_template("extract.html",error=error)
    else:
        error="Nie znaleziono produktu o podanym id"
        return render_template("extract.html",error=error)
    all_opinions=[]
    while next_page:
        print(next_page)
        if next_page:
            response = requests.get(next_page,headers=headers)
            if response.status_code == 200:
                page_dom = BeautifulSoup(response.text,"html.parser")
                opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
                for opinion in opinions:
                    single_opinion = {
                        key: utils.extract_feature(opinion, *value)
                        for key,value in utils.selectors.items()
                    }
                    all_opinions.append(single_opinion)
                try:
                    next_page = "https://www.ceneo.pl"+utils.extract_feature(page_dom,"a.pagination__next","href")
                except TypeError:
                    next_page = None
            else: print(response.status_code)
    if not os.path.exists("./app/data"):
        os.mkdir("./app/data")
    if not os.path.exists("./app/data/opinions"):
        os.mkdir("./app/data/opinions")
    with open(f"./app/data/opinions/{product_id}.json",'w',encoding="UTF8") as jf:
        json.dump(all_opinions, jf, indent=4,ensure_ascii=False)
    
    #konwersja
    opinionss = pd.read_json(f"./app/data/opinions/{product_id}.json")
    opinionss.stars = opinionss.stars.apply(lambda s: s.split("/")[0].replace(",",".")).astype(float)
    opinionss.useful=opinionss.useful.astype(int)
    opinionss.unuseful=opinionss.unuseful.astype(int)
    
    #liczba opinii
    opinionss_count = len(opinionss)
    #liczba wad
    cons_count = opinionss["cons"].astype(bool).sum()
    unique_cons_count =len(opinionss.cons.explode().dropna().value_counts())
    #liczba zalet
    pros_count = opinionss["pros"].astype(bool).sum()
    
    unique_pros_count = len(opinionss.pros.explode().dropna().value_counts())
    
    #średnia liczba gwiazdek
    averages_stars = round(opinionss.stars.mean(),2)

    opinion_short={
        "id produktu":product_id,
        "liczba opinii":f"{opinions_count}",
        "liczba wad":f"{cons_count}",
        "liczba zalet":f"{pros_count}",
        "srednia ocena":f"{averages_stars}"
    }
    if not os.path.exists("./app/data/opinions_short"):
        os.mkdir("./app/data/opinions_short")
    with open(f"./app/data/opinions_short/{product_id}_short.json",'w',encoding="UTF8") as jf:
        json.dump(opinion_short, jf, indent=4,ensure_ascii=False)
    
    return redirect(url_for('product', product_id=product_id,product_name=product_name))

@app.route("/products")
def products():
    path_to_json = 'app/data/opinions_short/'
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    jsons_data = pd.DataFrame(columns=[ 
                                        'liczba opinii',
                                        'liczba wad',
                                        'liczba zalet',
                                        'średnia ocena'])
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)

            id_produktu = json_text['id produktu']
            liczba_opinii = json_text['liczba opinii']
            liczba_wad = json_text['liczba wad']
            liczba_zalet = json_text['liczba zalet']
            srednia_ocena = json_text['srednia ocena']
            
            jsons_data.loc[id_produktu] = [
                                     liczba_opinii,
                                     liczba_wad,
                                     liczba_zalet,
                                     srednia_ocena]
    print(jsons_data)
    return render_template('products.html',opinions=jsons_data.to_html(table_id='opinions'))

@app.route("/author")
def author():
    return render_template('author.html')

@app.route("/product/<product_id>")
def product(product_id):
    product_name=request.args.get('product_name')
    opinions = pd.read_json(f"app/data/opinions/{product_id}.json")
    return render_template('product.html',product_id=product_id,product_name=product_name,opinions = opinions.to_html(table_id='opinions'))