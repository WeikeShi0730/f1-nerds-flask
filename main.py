from flask import Flask
import json
from matplotlib import pyplot as plt
import fastf1 as ff1
from fastf1 import plotting
from fastf1 import api

app = Flask(__name__)


@app.route("/")
def index():
    api.Cache.enable_cache("./")
    session = ff1.get_session(2021, "Monza", "Q")
    # quali.drivers
    print(session.results)
    return json.dumps(session.results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
