from flask import Flask, render_template, request, redirect
import threading
from bot import start_bot, stop_bot

app = Flask(__name__)
bot_thread = None

@app.route("/", methods=["GET", "POST"])
def index():
    global bot_thread

    if request.method == "POST":
        action = request.form.get("action")

        if action == "start":
            cookies = request.form["cookies"]
            uid = request.form["uid"]
            speed = int(request.form["speed"])
            messages = request.form["messages"].splitlines()

            bot_thread = threading.Thread(
                target=start_bot,
                args=(cookies, uid, messages, speed),
                daemon=True
            )
            bot_thread.start()

        if action == "stop":
            stop_bot()

        return redirect("/")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
