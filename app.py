from flask import Flask, render_template, request
import google.generativeai as genai
import os
import markdown
import textblob
import json
import re



app = Flask(__name__) # erm apparently this is some signing thingy, e.g. for  apps to access like video camera or whatever 

# get static folder 
static_folder_path = os.path.join(app.root_path, 'static')
food_data_file = os.path.join(static_folder_path,'food_data.json')

with open(food_data_file, 'r') as file:
    food_data = json.load(file)


food_items_str='['
food_items_list = list(food_data.keys())
for f in range(len(food_items_list)-1):
    food_items_str=food_items_str + '"' + food_items_list[f].title() + '",'
food_items_str = food_items_str + '"' + food_items_list[-1].title() + '"]'
print("ff")
print(food_items_str)


@app.route("/", methods=["GET","POST"])  # that @ is a deocorator - which makes the app.route run before the index function 
def index():
    return(render_template("index.html"))
    
    
    
@app.route("/food_info", methods=["GET","POST"]) 
def food_info():
    return(render_template("food_info.html", f = food_items_str))



@app.route("/generate_shopping_list", methods=["GET","POST"])  # that @ is a deocrator - which makes the app.route run before the index function 
def generate_shopping_list():

#    form_data = request.get_json()
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
        rep_str = '<a href=# onclick=get_food_date("' + k +'")' + '>' + k.title() + '</a>'
        proc_html = re.sub(k, rep_str, proc_html, flags=re.IGNORECASE)
    return(render_template("shopping_list.html", r = proc_html))


@app.route("/subscription",methods=["GET","POST"])
def subscription():
    return(render_template("subscription.html"))

@app.route("/thankyou", methods=["GET"])
def thankyou():
    r = model.generate_content() 
    return render_template("thankyou.html", r=r)



model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key="AIzaSyDQvy9nXbikgMd890MAyt-penTiMoM7Vek")
if __name__ == "__main__": # apparently, this checks if the thingy is being run onto the cloud? 
    app.run()

