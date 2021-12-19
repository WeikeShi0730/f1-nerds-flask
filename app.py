from flask import Flask
import json
import pandas as pd
from matplotlib import pyplot as plt
import fastf1 as ff1
from fastf1 import plotting
from fastf1 import api

app = Flask(__name__)
api.Cache.enable_cache("./")

# session result
@app.route("/api/year/<year>/weekend/<weekend>/session/<session>")
def session_result(year, weekend, session):
    session = ff1.get_session(year, weekend, session)
    return json.dumps(session.results)


# driver laps
@app.route("/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>")
def driver_laps(year, weekend, session, driver):
    laps = ff1.get_session(year, weekend, session).load_laps()
    driver = laps.pick_driver(driver)
    laps_time = driver["LapTime"]
    laps_number = driver["LapNumber"]
    laps_tire = driver["Compound"]
    laps_concat = pd.concat([laps_number, laps_time, laps_tire], axis=1)

    return laps_concat.to_json()


# driver lap telemetry
@app.route(
    "/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>/lap/<lap>"
)
def driver_lap(year, weekend, session, driver, lap):
    lap = int(lap)
    laps = ff1.get_session(year, weekend, session).load_laps(with_telemetry=True)
    laps_driver = laps.pick_driver(driver)
    lap_driver = laps_driver.iloc[lap - 1 : lap, :].pick_fastest()

    telemetry_cache = lap_driver.telemetry
    if not telemetry_cache.empty:
        lap_telemetry = telemetry_cache
    else:
        lap_telemetry = lap_driver.get_car_data()
    telemetry_speed = lap_telemetry["Speed"]
    telemetry_throttle = lap_telemetry["Throttle"]
    telemetry_brake = lap_telemetry["Brake"]
    telemetry_rpm = lap_telemetry["RPM"]
    telemetry_gear = lap_telemetry["nGear"]
    telemetry_drs = lap_telemetry["DRS"]
    telemetry_concat = pd.concat(
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
    # with pd.option_context("display.max_rows", None, "display.max_columns", None):
    #     print(telemetry_speed)
    return telemetry_concat.to_json()
    # return lap.to_json()


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
