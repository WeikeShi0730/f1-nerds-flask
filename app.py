from flask import Flask, jsonify
from flask_caching import Cache
import pandas as pd
from matplotlib import pyplot as plt
import fastf1 as ff1
from fastf1 import plotting
from fastf1 import api
from rq import Queue
from rq.job import Job
from worker import conn, redis_url

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_REDIS_URL": redis_url,
    "CACHE_DEFAULT_TIMEOUT": 500,
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
# cache.clear()
q = Queue(connection=conn)

@app.route("/")
def index():
    return "index"


# session result
@app.route("/api/year/<year>/weekend/<weekend>/session/<session>", methods=["GET"])
def session_result(year, weekend, session):
    id = year + "-" + weekend + "-" + session
    cached_session = cache.get(id)
    if cached_session is None:
        session_results_data = ff1.get_session(year, weekend, session)
        cache.set(id, session_results_data)
    else:
        session_results_data = cached_session

    return jsonify(session_results_data.results)


# driver laps
@app.route(
    "/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>",
    methods=["GET"],
)
def driver_laps(year, weekend, session, driver):
    id = year + "-" + weekend + "-" + session + "-" + driver
    cached_driver_laps = cache.get(id)
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
        cache.set(id, driver_laps_data)
    else:
        driver_laps_data = cached_driver_laps

    return driver_laps_data.to_json()


# driver lap telemetry
@app.route(
    "/api/year/<year>/weekend/<weekend>/session/<session>/driver/<driver>/lap/<lap>",
    methods=["GET"],
)
def driver_lap(year, weekend, session, driver, lap):
    job_id = year + "-" + weekend + "-" + session + "-" + driver + "-" + lap
    try:

        cached_driver_laps = Job.fetch(job_id, connection=conn)
        job_status = cached_driver_laps.get_status()
        if job_status == "finished":
            return cached_driver_laps.result.to_json()
        elif job_status == "failed":
            registry = q.failed_job_registry
            registry.requeue(job_id)
            return jsonify(job_status)
        else:
            return jsonify(job_status)
    except:
        new_job = q.enqueue(
            get_driver_lap_data,
            args=(year, weekend, session, driver, lap),
            job_id=job_id,
        )
        return jsonify(new_job.id)


def get_driver_lap_data(year, weekend, session, driver, lap):
    lap = int(lap)
    session_data = cache.get(year + "-" + weekend + "-" + session)
    if session_data is not None:
        laps = session_data.load_laps(with_telemetry=True)
    else:
        laps = ff1.get_session(year, weekend, session).load_laps(with_telemetry=True)
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
    return telemetry_data


if __name__ == "__main__":
    app.run()
