# doing necessary imports

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo


app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/',methods=['GET'])
@cross_origin()
def homePage():
	return render_template("index.html")

@app.route("/results",methods=["POST","GET"])
def index():
    if request.method == "POST":
        searchString = request.form['content'].replace(" ","+")
        try:

            # dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            # db = dbConn['crawlerDB']
            # all_reviews = db[searchString].find({})
            all_reviews = []

            # if all_reviews.count()>0:
            #     return render_template('results.html',all_reviews=all_reviews)
            # else:
            url = "https://www.flipkart.com/search?q=" + searchString

            html_string = requests.get(url).content
            soup = bs(html_string, 'html.parser')

            bigboxes = soup.find_all("div", {'class': '_2kHMtA'})
            if len(bigboxes) == 0:
                bigboxes = soup.find_all("div", {'class': '_4ddWXP'})
                if len(bigboxes) == 0:
                    bigboxes = soup.find_all("div", {'class': '_1xHGtK _373qXS'})
                    if len(bigboxes) == 0:
                        return render_template("error.html")

                # table = db[searchString]

            all_reviews = []
            for i in range(len(bigboxes)):
                product_Link = "https://www.flipkart.com" + bigboxes[i].a['href']
                #     print(product_Link)
                product_html = requests.get(product_Link).content
                prod_soup = bs(product_html, 'html.parser')

                reviews = prod_soup.find_all("div", {'class': 'col _2wzgFH'})
                #     print(len(reviews))
                for review in reviews:
                    try:
                        prod_name = prod_soup.find('span', {'class': 'B_NuCI'}).text
                            # print(prod_name)
                    except:
                        print("Something Wrong")

                    try:
                        rating = review.div.find("div", {'class': '_3LWZlK _1BLPMq'}).text
                        #             print(rating)
                    except:
                        rating = "No Rating"

                    try:
                        commentHead = review.div.find('p', {'class': '_2-N8zT'}).text
                        #             print(commentHead)
                    except:
                            print("No comment")

                    try:
                        commentbody = review.find_all('div')[2].div.div.div.text
                        #             print(commentbody)
                    except:
                        print("No comments")
                    try:
                        cust_name = review.find('div', {'class': 'row _3n8db9'}).div.p.text
                        #             print(cust_name)
                    except:
                        print("Flipkart Customer")

                    mydict = {"Keyword_searched": searchString, "Product": prod_name, "Customer_Name": cust_name,
                                    "Rating": rating, "CommentHead": commentHead,
                                    "Comment": commentbody}

                    # x = table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                    all_reviews.append(mydict)

            return render_template('results.html', all_reviews=all_reviews)  # showing the review to the user
        except:
            return render_template("error.html")
    else:
        return render_template('index.html')

@app.route("/error")
def error_page():
    return render_template("error.html")

if __name__ == "__main__":
    app.run(port=8000,debug=True) # running the app on the local machine on port 8000