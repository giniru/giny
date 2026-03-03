import base64
import random
import requests
from seleniumbase import SB


def get_geo_data():
    """Retrieve geolocation and timezone information."""
    data = requests.get("http://ip-api.com/json/").json()
    return {
        "lat": data["lat"],
        "lon": data["lon"],
        "timezone": data["timezone"],
        "lang": data["countryCode"].lower()
    }


def decode_channel_name(encoded_name: str) -> str:
    """Decode a Base64-encoded Twitch channel name."""
    return base64.b64decode(encoded_name).decode("utf-8")


def handle_cookie_buttons(driver):
    """Click common cookie/consent buttons if present."""
    if driver.is_element_present('button:contains("Accept")'):
        driver.cdp.click('button:contains("Accept")', timeout=4)


def handle_start_watching(driver):
    """Click 'Start Watching' if present."""
    if driver.is_element_present('button:contains("Start Watching")'):
        driver.cdp.click('button:contains("Start Watching")', timeout=4)
        driver.sleep(10)


def open_secondary_driver(url, timezone, geoloc):
    """Open a second undetectable driver instance."""
    secondary = driver.get_new_driver(undetectable=True)
    secondary.activate_cdp_mode(url, tzone=timezone, geoloc=geoloc)
    secondary.sleep(10)

    handle_start_watching(secondary)
    handle_cookie_buttons(secondary)

    return secondary


# -----------------------------
# Main Script
# -----------------------------

geo = get_geo_data()
latitude = geo["lat"]
longitude = geo["lon"]
timezone_id = geo["timezone"]

proxy_str = False

encoded_name = "YnJ1dGFsbGVz"
channel_name = decode_channel_name(encoded_name)
twitch_url = f"https://www.twitch.tv/{channel_name}"

while True:
    with SB(
        uc=True,
        locale="en",
        ad_block=True,
        chromium_arg="--disable-webgl",
        proxy=proxy_str
    ) as driver:

        random_delay = random.randint(450, 800)

        driver.activate_cdp_mode(
            twitch_url,
            tzone=timezone_id,
            geoloc=(latitude, longitude)
        )

        driver.sleep(2)
        handle_cookie_buttons(driver)
        driver.sleep(2)

        driver.sleep(12)
        handle_start_watching(driver)
        handle_cookie_buttons(driver)

        # Check if the stream is live
        if driver.is_element_present("#live-channel-stream-information"):

            handle_cookie_buttons(driver)

            # Open secondary viewer
            secondary_driver = driver.get_new_driver(undetectable=True)
            secondary_driver.activate_cdp_mode(
                twitch_url,
                tzone=timezone_id,
                geoloc=(latitude, longitude)
            )

            secondary_driver.sleep(10)
            handle_start_watching(secondary_driver)
            handle_cookie_buttons(secondary_driver)

            driver.sleep(random_delay)

        else:
            break
