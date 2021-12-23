from flask import Flask
from flask_caching import Cache
import json
import pandas as pd
from matplotlib import pyplot as plt
import fastf1 as ff1
from fastf1 import plotting
from fastf1 import api

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

# api.Cache.enable_cache("./")

# session result
@app.route("/api/year/<year>/weekend/<weekend>/session/<session>")
def session_result(year, weekend, session):
    cached_session = cache.get(year + "-" + weekend + "-" + session)
    if cached_session is None:
        print("NO Cache!!!")
        session_data = ff1.get_session(year, weekend, session)
        cache.set(year + "-" + weekend + "-" + session, session_data)
    else:
        print("Yes Cache!!!")
        session_data = cached_session

    return json.dumps(session_data.results)


# driver laps
@app.route("/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>")
def driver_laps(year, weekend, session, driver):
    cached_driver_laps = cache.get(year + "-" + weekend + "-" + session + "-" + driver)
    if cached_driver_laps is None:
        session_data = cache.get(year + "-" + weekend + "-" + session)
        if session_data is not None:
            laps = session_data.load_laps()
        else:
            laps = ff1.get_session(year, weekend, session).load_laps()
        driver_data = laps.pick_driver(driver)
        laps_time = driver_data["LapTime"]
        laps_number = driver_data["LapNumber"]
        laps_tire = driver_data["Compound"]
        driver_laps_data = pd.concat([laps_number, laps_time, laps_tire], axis=1)
        cache.set(year + "-" + weekend + "-" + session + "-" + driver, driver_laps_data)
    else:
        driver_laps_data = cached_driver_laps

    return driver_laps_data.to_json()


# driver lap telemetry
@app.route(
    "/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>/lap/<lap>"
)
def driver_lap(year, weekend, session, driver, lap):
    cached_driver_laps = cache.get(
        year + "-" + weekend + "-" + session + "-" + driver + "-" + lap
    )
    if cached_driver_laps is None:
        print("NO Cache!!!")
        lap = int(lap)
        session_data = cache.get(year + "-" + weekend + "-" + session)
        if session_data is not None:
            laps = session_data.load_laps(with_telemetry=True)
        else:
            laps = ff1.get_session(year, weekend, session).load_laps(
                with_telemetry=True
            )
        laps_driver = laps.pick_driver(driver)
        lap_driver = laps_driver.iloc[lap - 1 : lap, :].pick_fastest()
        lap_telemetry = lap_driver.get_car_data()
        telemetry_speed = lap_telemetry["Speed"]
        telemetry_throttle = lap_telemetry["Throttle"]
        telemetry_brake = lap_telemetry["Brake"]
        telemetry_rpm = lap_telemetry["RPM"]
        telemetry_gear = lap_telemetry["nGear"]
        telemetry_drs = lap_telemetry["DRS"]
        telemetry_data = pd.concat(
            [
                telemetry_speed,
                telemetry_rpm,
                telemetry_throttle,
                telemetry_brake,
                telemetry_gear,
                telemetry_drs,
            ],
            axis=1,
        )
        cache.set(
            year + "-" + weekend + "-" + session + "-" + driver + "-" + str(lap),
            telemetry_data,
        )
    else:
        print("Yes Cache!!!")
        telemetry_data = cached_driver_laps

    return telemetry_data.to_json()


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
