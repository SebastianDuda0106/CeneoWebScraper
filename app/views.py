from app import app

import requests,os,json
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
    #
    #headers = {
    #    "Cookie":"__RequestVerificationToken=xJq5TBYbsboqT6V1EcjTrBFlkonIs0hok4KqL9qCDNYo3Q2ie-T_lxcXSp7aaBTBrp2j3QrIZO_uYE0EV6C-Hdjo0MH0e3dd9vX0QnJkg9I1; st2=sref%3dhttps%3a%2f%2fwww.bing.com%2f%2c_t%3d63880399794%2cencode%3dtrue; __utmf=cfd9ce0045cb6dd6b6857cb26744adde_Dsgqi6QMc9CtX7buqOpcIw%3D%3D; sv3=1.0_5b56db08-1aa5-11f0-9ba7-fb4515694512; userCeneo=ID=92e2eb0d-31c7-42eb-af39-bad7fbe73b13; ai_user=MZY2|2025-04-16T09:29:55.097Z; appType=%7B%22Value%22%3A1%7D; cProdCompare_v2=; browserBlStatus=0; ga4_ga=GA1.2.5b56db08-1aa5-11f0-9ba7-fb4515694512; _gcl_au=1.1.218874479.1744795798; consentcookie=eyJBZ3JlZUFsbCI6dHJ1ZSwiQ29uc2VudHMiOlsxLDMsNCwyXSwiVENTdHJpbmciOiJDUVA5WDRBUVA5WDRBR3lBQkJQTEJsRXNBUF9nQUFBQUFCNVlJTnBEN0JiQkxVRkF3RmhqWUtzUU1JRVRVTUNBQW9RQUFBYUJBQ0FCUUFLUUlBUUNra0FRQkFTZ0JBQUNBQUFBSUNSQklRQU1BQUFBQ0VBQVFBQUFJQUFFQUFDUUJRQUlBQUFBZ0FBUUFBQVlBQUFpQUlBQUFBQUlnQUlBRUFBQW1RaEFBQUlBRUVBQWhBQUVJQUFBQUFBQUFBQUFBZ0FBQUFBQ0FBSUFBQUFBQUNBQUFJSU5nQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUJZS0FEQUFFRUd3a0FHQUFJSU5ob0FNQUFRUWJFUUFZQUFnZzJLZ0F3QUJCQnNaQUJnQUNDRFk2QURBQUVFR3lFQUdBQUlJTmtvQU1BQVFRYktRQVlBQWdnMldnQXdBQkJCc0EiLCJWZXJzaW9uIjoidjMifQ==; FPID=FPID2.2.uQSZi7Ny4y7L5b8%2F8v4yQih7ehY0fAU3fgTeRgOzirg%3D; FPLC=3mxrIDitbrynAmMqiQljNLv1w7Fk1s1V4IUWfur54duV5RiujsmNx9IEm2yo8OibVbBX%2BE9icqHn3h031g1gEH0qi5FoyPIPEQvK%2FSjxrPPtElQ%3D; nps3=SessionStartTime=1744795806,SurveyId=64; _tt_enable_cookie=1; _ttp=01JRYYYDFJ2H9KAVDM9DZ4NPF9_.tt.1; _fbp=fb.1.1744795810144.917175535874715790; tc=testName=ProductSetsButtonsABTest&testVariant=1&testType=98&activeTest=ProductSetsButtonsABTest; __gads=ID=4118089efceba044:T=1744795856:RT=1744795856:S=ALNI_MaLf9_JnPwNfQPqZFrFf3jg9sL3Dg; __gpi=UID=0000107f803297a0:T=1744795856:RT=1744795856:S=ALNI_MaWd9MDZ9VAwQ3lwbgXs4mJpMh79A; rc=igdamb4ThOT/AObseYIgrJY43ABi+EowVwqG1/sk7hHXTyRYrl8iMH4Lih1EatSs2mqKU2ccZhxqCCzPpHPgY3KXyZmmd9gZecWDzM7KgOHc9rMUj2eCHpY43ABi+EowVwqG1/sk7hHXTyRYrl8iMHCKlbKzeUNk; ai_session=Lf61v|1744795795912|1744795877452.8; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22bxd5jSBPhF4tpGrKODqs%22%2C%22expiryDate%22%3A%222026-04-16T09%3A31%3A18.195Z%22%7D; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222026-04-16T09%3A31%3A18.199Z%22%7D; ga4_ga_K2N2M0CBQ6=GS1.2.1744795795.1.1.1744795878.0.0.815426031; ttcsid_CNK74OBC77U1PP7E4UR0=1744795809275.1.1744795878639; ttcsid=1744795809291.1.1744795878639",
    #    "Host":"www.ceneo.pl",
    #    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
    #}
    #selectors = {
    #    "opinion_id":(None,'data-entry-id'),
    #    "author":("span.user-post__author-name",),
    #    "recommendation":("span.user-post__author-recomendation > em",),
    #    "stars":("span.user-post__score-count",),
    #    "content":("div.user-post__text",),
    #    "pros":("div.review-feature__item--positive",None,True),
    #    "cons":("div.review-feature__item--negative",None,True),
    #    "useful":("button.vote-yes > span",),
    #    "unuseful":("button.vote-no > span",),
    #    "post_date":("span.user-post__published > time:nth-child(1)",'datetime'),
    #    "purchase_date":("span.user-post__published > time:nth-child(2)",'datetime')
    #    }
    #def extract(ancestor,selector=None,attribute=None,multiple=False):
    #    if selector:
    #        if multiple:
    #            if attribute:
    #                return [tag[attribute].strip() for tag in ancestor.select(selector)]
    #            return [tag.text.strip() for tag in ancestor.select(selector)]
    #        if attribute:
    #            try:
    #                return ancestor.select_one(selector)[attribute].strip()
    #            except TypeError:
    #                return None
    #        try:
    #            return ancestor.select_one(selector).text.strip()
    #        except AttributeError:
    #            return None
    #    if attribute:
    #        return ancestor[attribute].strip()
    #    return ancestor.text.strip()
    #
    product_id = request.form.get('product_id')
    next_page=f"https://www.ceneo.pl/{product_id}#tab=reviews"
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

    return redirect(url_for('product', product_id=product_id))

@app.route("/products")
def products():
    return render_template('products.html')

@app.route("/author")
def author():
    return render_template('author.html')

@app.route("/product/<product_id>")
def product(product_id):
    return render_template('product.html',product_id=product_id)