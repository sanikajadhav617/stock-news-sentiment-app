from flask import Flask

app = Flask(_name_)

@app.route("/")
def home():
    return "Hello! Stock News App is Working ✅"

if _name_ == "_main_":
    app.run()
