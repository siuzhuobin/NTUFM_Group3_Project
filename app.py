from flask import Flask, render_template, request
import google.generativeai as genai
import os
import markdown
from textblob import TextBlob
import json
import re
import urllib.parse
import numpy as np 

app = Flask(__name__) # erm apparently this is some signing thingy, e.g. for  apps to access like video camera or whatever 

# get static folder, and read list of food info
static_folder_path = os.path.join(app.root_path, 'static')
food_data_file = os.path.join(static_folder_path,'food_data.json')
SS_branches_file = os.path.join(static_folder_path,'SS_branches.json')
with open(food_data_file, 'r') as file:
    food_data = json.load(file)
with open(SS_branches_file, 'r') as file:
    SS_branches = json.load(file)


food_items_str = json.dumps(list(food_data.keys()))
SS_branch_regions_str = json.dumps(list(SS_branches.keys()))
nutritional_units = {
    "Calories": "kcal",
    "Protein": "g",
    "Fat": "g",
    "Carbohydrates": "g",
    "Fiber": "g",
    "Sugar": "g",
    "Sodium": "mg",
    "Potassium": "mg",
    "Vitamin C": "mg",
    "Calcium": "mg",
    "Iron": "mg"
}



@app.route("/", methods=["GET","POST"]) 
def index():
  return(render_template("index.html"))
 
@app.route("/get_guide", methods=["GET","POST"]) 
def get_guide():
  return(render_template("get_guide.html"))

@app.route("/subscription",methods=["GET","POST"])
def subscription():
    return(render_template("subscription.html"))

@app.route("/feedback",methods=["GET","POST"])
def feedback():
    return(render_template("feedback.html"))



@app.route("/food_info", methods=["GET","POST"]) 
def food_info():
    init_food = urllib.parse.unquote(request.args.get('food',''))
    print(f"SSbrs{SS_branch_regions_str}")
    return(render_template("food_info.html", food_items = food_items_str, \
                           init_food=f'"{init_food.title()}"',\
                           SS_branch_regions=SS_branch_regions_str))


@app.route("/get_food_info", methods=["GET","POST"]) 
def get_food_info():
#    food_item = urllib.parse.unquote(request.form.get('food','')).lower()
    food_item = request.form.get('food','').lower()
    if not (food_item in food_data.keys()): return ('Item not found')

    html = "<table border='1'>\n <tr>"
    html += "<th><strong>Nutrition</strong></th><th><strong>Quantity</strong></th></tr>\n"
    nutrition_data = food_data[food_item]
    for n in nutrition_data.items():
        (nutrition, qty) = n

        if (nutrition in nutritional_units):
            nutrition_unit = nutritional_units[nutrition]
        else:
            nutrition_unit = ''
        html += f"<tr><td>{nutrition}</td><td>{qty} {nutrition_unit}</td></tr>\n"
    html+="</table>\n"

    return(html)


@app.route("/get_food_offers", methods=["GET","POST"]) 
def get_food_offers():
    food_item = request.form.get('food','').lower()
    region = request.form.get('branch_region');

    if not region in list(SS_branches.keys()):
        return ''
    branches = SS_branches[region]

    print("Region")
    print(region)
    print("branches")
    print(branches)

    avail_rate = min([abs(np.random.normal(0.9, 0.2)),1])
    offer_rate = min([abs(np.random.normal(0.5, 0.2)),1])

    no_branches = len(branches)
    rand_avail = np.random.uniform(0, 1, no_branches)
    rand_offer = np.random.uniform(0, 1, no_branches)

    avail = list(map(lambda r: r < avail_rate, rand_avail))
    offer = list(map(lambda r: r < offer_rate, rand_offer))
    
    yesno = {True:"Yes", False: "No"}

    html = "<table border='1'>\n <tr>"
    html += "<th><strong>Branch</strong><th><strong>Available</strong></th><th><strong>Offer</strong></th></tr>\n"
    for b in range(no_branches):
        html+='<tr>'
        branch = branches[b]
        avail_in_branch = avail[b]
        offer_in_branch = avail[b] and offer[b]
        html += f"<tr><td>{branch}</td><td>{yesno[avail_in_branch]}</td><td>{yesno[offer_in_branch]}</td></tr>\n"
    html += "<table>\n"
    return(html)

    

    
    



@app.route("/generate_shopping_list", methods=["GET","POST"])  
def generate_shopping_list():
    form_data = json.loads(request.form.get('json_str'))
    
    user_race = form_data['race']
    user_diet = form_data['diet']
    user_allergies = form_data['allergies']

    request_str = 'Please generate a healthy shopping list for a ' + user_race + ' individual on a ' + user_diet + ' diet.'
    allergy_count = len(user_allergies)
    if (allergy_count == 0):
        allergy_str = ''
    else:
        allergy_str = ' Please avoid ' 
        for a in range(0, allergy_count-1):
            allergy_str = allergy_str + user_allergies[a] 
            if (a < allergy_count -2):
                allergy_str = allergy_str +', '
            else:
                allergy_str = allergy_str +' and '
        
        allergy_str = allergy_str + user_allergies[-1] + '.'
    request_str = request_str + allergy_str
    result_str = request_str
    raw_html = markdown.markdown(model.generate_content(request_str).text)
    
    proc_html = raw_html
    for k in food_data.keys():
        rep_str = f'<a href=# onclick=get_food_info("{urllib.parse.quote(k)}")>{k.title()}</a>'
        proc_html = re.sub(k, rep_str, proc_html, flags=re.IGNORECASE)


    return(render_template("shopping_list.html", r = proc_html))


@app.route("/thankyou", methods=["GET","POST"])
def thankyou():
    origin = request.args.get('org')
    if (not origin):
        salutation = request.form.get('salutation')
        first_name =  request.form.get('First Name')
        last_name =  request.form.get('Last Name')
        email = request.form.get('email')
        track = request.form.get('INXMAIL_TRACKINGPERMISSION')

        track_str = 'not' if (not track) else ''

        r_str = f'<p> Thank you {salutation} {last_name}, {first_name} for \
            signing up with our newsletter, which will be delivered to {email}. </p><p>  \
            We have also noted your preference to {track_str} have your personal behavior tracked. </p>' 
        

        return render_template("thankyou.html", r=r_str)
    elif (origin=='feedback'):
        feedback_text = request.form.get('feedback')
        sentiment = TextBlob(feedback_text).sentiment
        if (sentiment.polarity > 0):
            r_str = 'Thank you for your nice feedback. We are glad you had a great experience with us.'
        else:
            r_str = 'We are sorry for your unpleasant experience. We will work harder next time. '
        return render_template("thankyou.html", r=r_str)


model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key="AIzaSyDQvy9nXbikgMd890MAyt-penTiMoM7Vek")
if __name__ == "__main__": # apparently, this checks if the thingy is being run onto the cloud? 
    app.run(debug=True)

