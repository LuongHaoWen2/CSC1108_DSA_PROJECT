from flask import Flask, render_template
import json 

app = Flask(__name__)

with open("data/airline_routes.json" , "r",encoding="utf-8") as f:
    airports=json.load(f)

airport_code = []



@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)