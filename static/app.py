from flask import Flask, render_template, request
import google.generativeai as genai
import os
import markdown
import textblob
import json


api_key="AIzaSyDQvy9nXbikgMd890MAyt-penTiMoM7Vek"  # aiyah by right supposed to be environmetal var; by left whatever lah 

model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key="AIzaSyDQvy9nXbikgMd890MAyt-penTiMoM7Vek")

app = Flask(__name__) # erm apparently this is some signing thingy, e.g. for  apps to access like video camera or whatever 


@app.route("/", methods=["GET","POST"])  # that @ is a deocrator - which makes the app.route run before the index function 
def index():
    return(render_template("index.html"))


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
    result_str = markdown.markdown(model.generate_content(request_str).text)
    
    return(render_template("shopping_list.html", r = result_str))

if __name__ == "__main__": # apparently, this checks if the thingy is being run onto the cloud? 
    app.run()


