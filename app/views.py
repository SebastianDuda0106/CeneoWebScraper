from app import app

import requests,os,json,csv
import pandas as pd
from flask import render_template,request,redirect,url_for,send_file
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from app.config import headers
from app import utils

import matplotlib
matplotlib.use('Agg')

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
    if not os.path.isfile(f"./app/data/opinions/{product_id}.json"):
        opinions_exists=False
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

    if not os.path.exists(f"./app/data/opinions/{product_id}.csv"):
        with open(f"./app/data/opinions/{product_id}.json",'r',encoding="UTF8") as jf:
            df=pd.read_json(jf)

        with open(f"./app/data/opinions/{product_id}.csv",'w',encoding="UTF8") as csf:
            df.to_csv(csf)
    
    if not os.path.exists(f"./app/data/opinions/{product_id}.xlsx"):
        pd.read_json(f"./app/data/opinions/{product_id}.json",encoding="UTF8").to_excel(f"./app/data/opinions/{product_id}.xlsx")
        
    else:
        opinions_exists=True
    if not os.path.isfile(f"./app/data/products/{product_id}_short.json"):
    #konwersja
        if opinions_exists:
            opinionss = pd.read_json(f"./app/data/opinions/{product_id}.json")
        else:
            opinionss = pd.DataFrame.from_dict(all_opinions)
        opinionss.stars = opinionss.stars.apply(lambda s: s.split("/")[0].replace(",",".")).astype(float)
        opinionss.useful=opinionss.useful.astype(int)
        opinionss.unuseful=opinionss.unuseful.astype(int)
        
        #liczba opinii
        opinionss_count = len(opinionss)
        #liczba wad
        cons_count = int(opinionss["cons"].astype(bool).sum())
        unique_cons_count =opinionss.cons.explode().dropna().value_counts().to_dict()
        #liczba zalet
        pros_count = int(opinionss["pros"].astype(bool).sum())
        
        unique_pros_count = opinionss.pros.explode().dropna().value_counts().to_dict()

        #rekomendacje
        recommendations = opinionss["recommendation"].value_counts(dropna=False).reindex(['Nie polecam','Polecam',None],fill_value=0).to_dict()
        #średnia liczba gwiazdek
        averages_stars = round(opinionss.stars.mean(),2)

        stats={
            "product_id":product_id,
            "product_name":product_name,
            "opinions_count":opinions_count,
            "cons_count":cons_count,
            "liczba unikatowych wad":unique_cons_count,
            "liczba zalet":pros_count,
            "liczba unikatowych zalet":unique_pros_count,
            "average_stars":averages_stars,
            "recommendations":recommendations
        }
        if not os.path.exists("./app/data/products"):
            os.mkdir("./app/data/products")
        with open(f"./app/data/products/{product_id}_short.json",'w',encoding="UTF8") as jf:
            json.dump(stats, jf, indent=4,ensure_ascii=False)
        
    return redirect(url_for('product', product_id=product_id,product_name=product_name))
    
@app.route("/products")
def products():
    products_files=os.listdir('app/data/products/')
    products_list = []
    for filename in products_files:
        with open(f"app/data/products/{filename}","r",encoding="UTF-8") as jf:
            product = json.load(jf)
            products_list.append(product)
    return render_template("products.html",products=products_list)
    #path_to_json = 'app/data/products/'

    #json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    #jsons_data = pd.DataFrame(columns=[ 
    #                                    'liczba opinii',
    #                                    'liczba wad',
    #                                    'liczba zalet',
    #                                    'średnia ocena'])
    #for index, js in enumerate(json_files):
    #    with open(os.path.join(path_to_json, js)) as json_file:
    #        json_text = json.load(json_file)
    #
    #        id_produktu = json_text['id produktu']
    #        liczba_opinii = json_text['liczba opinii']
    #        liczba_wad = json_text['liczba wad']
    #        liczba_zalet = json_text['liczba zalet']
    #        srednia_ocena = json_text['srednia ocena']
    #        
    #        jsons_data.loc[id_produktu] = [
    #                                 liczba_opinii,
    #                                 liczba_wad,
    #                                 liczba_zalet,
    #                                 srednia_ocena]
    #print(jsons_data)
    #return render_template('products.html',opinions=jsons_data.to_html(table_id='opinions'))

@app.route("/charts/<product_id>")
def charts(product_id):
    if not os.path.exists("app/static/images"):
        os.mkdir("app/static/images")
    if not os.path.exists("app/static/images/charts"):
        os.mkdir("app/static/images/charts")
    
    with open(f"app/data/products/{product_id}_short.json","r", encoding="UTF-8") as jf:
        stats= json.load(jf)
    recommendations = pd.Series(stats["recommendations"])
    recommendations.plot.pie(
        label="",
        title="Rozkład rekomendacji w opiniach o produkcie",
        labels=['Nie polecam','Polecam',"Nie mam zdania"],
        colors=["crimson","forestgreen","lightgray"],
        autopct="%1.1f%%"
    )
    plt.savefig(f"app/static/images/charts/{stats['product_id']}_pie.png")
    plt.close()
    return render_template("charts.html", product_id=product_id,product_name=stats['product_name'])

@app.route("/charts2/<product_id>")
def charts2(product_id):
    if not os.path.exists("app/static/images"):
        os.mkdir("app/static/images")
    if not os.path.exists("app/static/images/charts"):
        os.mkdir("app/static/images/charts")
    
    with open(f"app/data/products/{product_id}_short.json","r", encoding="UTF-8") as jf:
        stats= json.load(jf)
    recommendations = pd.Series(stats["recommendations"])
    recommendations.plot.pie(
        label="",
        title="Rozkład rekomendacji w opiniach o produkcie",
        labels=['Nie polecam','Polecam',"Nie mam zdania"],
        colors=["crimson","forestgreen","lightgray"],
        autopct="%1.1f%%"
    )
    plt.savefig(f"app/static/images/charts/{stats['product_id']}_pie.png")
    plt.close()

    categories = ['Nie polecam','Polecam','Nie mam zdania']
    plt.bar(categories,recommendations.values)
    plt.savefig(f"app/static/images/charts/{stats['product_id']}_bar.png")
    plt.close

    return render_template("charts2.html", product_id=product_id,product_name=stats['product_name'])

@app.route("/author")
def author():
    return render_template('author.html')

@app.route("/product/<product_id>")
def product(product_id):
    product_name=request.args.get('product_name')
    opinions = pd.read_json(f"app/data/opinions/{product_id}.json")
    return render_template('product.html',product_id=product_id,product_name=product_name,opinions = opinions.to_html(table_id='opinions'))

@app.route("/download_json/<product_id>")
def download_json(product_id): 
    return send_file(f'./data/opinions/{product_id}.json', as_attachment=True)

@app.route("/download_csv/<product_id>")
def download_csv(product_id):
    if not os.path.exists(f"./app/data/opinions/{product_id}.csv"):
        with open(f"./app/data/opinions/{product_id}.json",'r',encoding="UTF8") as jf:
            df=pd.read_json(jf)

        with open(f"./app/data/opinions/{product_id}.csv",'w',encoding="UTF8") as csf:
            df.to_csv(csf)
    
    return send_file(f'./data/opinions/{product_id}.csv', as_attachment=True)

@app.route("/download_xlsx/<product_id>")
def download_xlsx(product_id): 
    if not os.path.exists(f"./app/data/opinions/{product_id}.xlsx"):
        pd.read_json(f"./app/data/opinions/{product_id}.json",encoding="UTF8").to_excel(f"./app/data/opinions/{product_id}.xlsx")
        
    return send_file(f'./data/opinions/{product_id}.xlsx', as_attachment=True)