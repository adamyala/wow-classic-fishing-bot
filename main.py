import time
from datetime import datetime

import numpy
import pyautogui
from PIL import Image

DEBUG = False
ERROR_SENSITIVITY = 1.4
LOCATION = "booty-bay"
LOCATOR_CONFIDENCE = 0.35


def get_cropped_screen(left, top, right, bottom):
    image = pyautogui.screenshot()

    cropped_image = image.crop((left, top, right, bottom))

    if DEBUG:
        cropped_image.save("cropped-image.png")

    print("cropped image size", cropped_image.size)

    return cropped_image


def get_bobber_center(left, top, target):
    target_center = pyautogui.center(target)
    center_x, center_y = target_center

    # we readd the x and y pixels that were cropped out
    true_center_x = center_x + left
    true_center_y = center_y + top

    print("bobber coords", true_center_x, true_center_y)

    return true_center_x, true_center_y


def watch_bobber(x, y):
    t_end = time.time() + 20
    bobber_region = (x - 50, y - 50, 150, 150)
    initial_bobber = pyautogui.screenshot(region=bobber_region)

    if DEBUG:
        initial_bobber.save("initial-bobber.png")

    initial_array = numpy.asarray(initial_bobber)
    count = 1
    threshold = 0

    while time.time() < t_end:
        print("watch", count)

        watched_bobber = pyautogui.screenshot(region=bobber_region)

        if DEBUG:
            watched_bobber.save("watched-bobber.png")

        watched_array = numpy.asarray(watched_bobber)
        image_diff = initial_array.astype("float") - watched_array.astype("float")
        err = numpy.sum(image_diff**2)
        err /= float(initial_array.shape[0] * initial_array.shape[1])

        if not threshold:
            threshold = err * ERROR_SENSITIVITY

        print("image_diff", err)
        count += 1

        if err > threshold:
            print("bobber moved")
            return True


def remove_items():
    for key in ["1", "2", "3", "4"]:
        for _ in range(40):
            pyautogui.press(key)
            time.sleep(1.5)


def main():
    screen = pyautogui.screenshot()
    print("screen size", screen.size)
    # -------------
    # | | | | | | |
    # -------------
    # | | | | | | |
    # -------------
    # | | |X|X| | |
    # -------------
    # | | | | | | |
    # -------------
    width, height = screen.size
    left = width * (1 / 3)
    top = height * (1 / 2)
    right = width * (2 / 3)
    bottom = height * (3 / 4)

    time.sleep(3)

    start_time = datetime.utcnow()

    while True:
        pyautogui.moveTo(200, 200)
        print("resetting cursor", datetime.now())

        # run macro to cast bobber
        pyautogui.press("=")
        print("casting bobber")
        time.sleep(2)

        cropped_image = get_cropped_screen(left, top, right, bottom)

        bobber_image_file = Image.open(f"zone_images/{LOCATION}.png")

        # look for the bobber. some zones work better with a different confidence level than others
        target = pyautogui.locate(
            needleImage=bobber_image_file,
            haystackImage=cropped_image,
            confidence=LOCATOR_CONFIDENCE,
        )
        if not target:
            print("not found")
            continue

        bobber_x, bobber_y = get_bobber_center(left, top, target)

        if DEBUG:
            pyautogui.moveTo(x=bobber_x / 2, y=bobber_y / 2)
        print("found it")

        bite = watch_bobber(bobber_x, bobber_y)
        if bite:
            pyautogui.rightClick(x=bobber_x / 2, y=bobber_y / 2)
            time.sleep(1)

        seconds_since_start = (datetime.utcnow() - start_time).seconds
        print(seconds_since_start, "since start")
        if seconds_since_start >= 1800:
            remove_items()
            start_time = datetime.utcnow()


main()
