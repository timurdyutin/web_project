from app import app

app.config["SECRET_KEY"] = "super_secret_key"
app.run(port=8080, host="localhost")