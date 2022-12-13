import requests
import json
from datetime import date
from fastapi import FastAPI
app = FastAPI()

def astro_data(q):
    curr_date = date.today()
    parameters = {
        "key": "aebc64afeb2e402982b00322220812",
        "q": str(q),
        "dt": curr_date
    }
    response = requests.get("https://api.weatherapi.com/v1/astronomy.json", params=parameters)
    data = response.json()
    return data


def current_time_in_timezone(timezone):
    parameters = {
        "timeZone": timezone
    }
    response = requests.get("https://www.timeapi.io/api/Time/current/zone", params=parameters)
    data = response.json()
    # print(data["hour"], data["minute"])
    return data["hour"], data["minute"]


def time_breaker(time):
    # xx:xx AM ...
    full_time = time
    if len(time) < 8:
        full_time = "0" + time
    # print(full_time, time)
    hour = full_time[0:2]
    minute = full_time[3:5]
    tod = full_time[6:8]
    return hour, minute, tod


def ampm_to_military_time(time):
    hour, minute, tod = time_breaker(time)
    if hour == 12 and tod == "AM":
        return "00", str(minute)
    elif tod == "AM":
        return hour, minute
    elif tod == "PM" and hour == "12":
        return hour, minute
    else:
        hour = str(int(hour) + 12)
        return hour, minute


def is_moon_visible(astro_response):
    moonrise = astro_response["astronomy"]["astro"]["moonrise"]
    moonset = astro_response["astronomy"]["astro"]["moonset"]
    moon_phase = astro_response["astronomy"]["astro"]["moon_phase"]
    moon_illumination = astro_response["astronomy"]["astro"]["moon_illumination"]
    timezone = astro_response["location"]["tz_id"]
    name = astro_response["location"]["name"]
    region = astro_response["location"]["region"]
    country = astro_response["location"]["country"]
    curr_h, curr_m = current_time_in_timezone(timezone)
    curr_h, curr_m = int(curr_h), int(curr_m)

    mrise_h, mrise_m = ampm_to_military_time(moonrise)
    mrise_h, mrise_m = int(mrise_h), int(mrise_m)

    mset_h, mset_m = ampm_to_military_time(moonset)
    mset_h, mset_m = int(mset_h), int(mset_m)
    print("Current Time:", curr_h, curr_m)
    print("Moonrise Time:", mrise_h, mrise_m)
    print("Moonset Time:", mset_h, mset_m)
    print("Moon Phase:", moon_phase)
    print("Moon Illumination:", moon_illumination)
    moon_status = "invisible"
    reason = "undefined"
    if curr_h == mrise_h and curr_m >= mrise_m:
        moon_status = "visible"
        reason = "same hour as the moonrise"
    elif curr_h == mset_h and curr_m < mset_m:
        moon_status = "visible"
        reason = "just before the moonset"
    elif mrise_h < curr_h < mset_h:
        moon_status = "visible"
        reason = "the moon has risen"
    elif moon_phase == "New Moon":
        moon_status = "invisible"
        reason = "the dark side of the moon"
    elif int(moon_illumination) <= 1:
        moon_status = "invisible"
        reason = "the moon has gone dark"
    else:
        moon_status = "invisible"
        reason = "the moon has not risen yet"
    output = {
        "name": name,
        "region": region,
        "country": country,
        "moonrise": moonrise,
        "moonset": moonset,
        "moon_phase": moon_phase,
        "moon_illumination": moon_illumination,
        "moon_status": moon_status,
        "reason": reason
    }
    return output
    # json_output = json.dumps(output, indent = 3)
    # return json_output


@app.get("/caniseethemoon")
def caniseethemoon(location):
    if location is None:
        text = "Input a zipcode."
    else:
        data = astro_data(location)
        text = is_moon_visible(data)
    return text


