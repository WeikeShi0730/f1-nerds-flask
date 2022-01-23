This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

### Development

To run the backend code in dev:

1. create a venv, and pip install packages
2. in different terminals run:
3. ```bash
   flask run
   ```
4. ```bash
   redis-server
   ```
5. ```bash
   python3 worker.py
   ```

### Production

The production code is hosted at Heroku:
[https://f1-nerds-flask.herokuapp.com/](https://f1-nerds-flask.herokuapp.com/)

### Introduction

This repo is the backend code for the web app [https://f1-nerds-next.vercel.app/](https://f1-nerds-next.vercel.app)

This code is to extract and process data from the [FastF1](https://theoehrly.github.io/Fast-F1/legacy.html) library written in Python. The endpoints are created for the frontend code to call and fetch processed data in JSON format.

Redis Cache is enabled to store data temporarily as fetching the data is expensive in this application.

Redis Queue and Worker is also used to fetch large data in the background without blocking other processes. While the large telemetry data is being fetched, the frontend would try to access the returned data in a poll fashion.

[Frontend repo](https://github.com/WeikeShi0730/f1-nerds-next)

### Usage

This web app is for F1 nerds who are not satisfied with only watching the live stream, and they need some more data to have a better understanding of what's going on the track!

Now it supports all races data since 2018. So go ahead select a year, Grand Prix weekend, session, drivers, and laps of your interest.

The graphs will show drivers' session details of each lap time and tire compounds.

Also, the telemetry data shows more detailed info for each lap, such as speed, RPM, throttle, brake, gear, and DRS. They will help you understand how the driver is doing in a specific lap.

You can also select laps from different years, Grand Prix, sessions, and drivers to have a more comprehensive comparison between several laps.

Enjoy!
