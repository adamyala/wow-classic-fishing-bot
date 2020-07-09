import os
import glob
from datetime import datetime, timedelta
import numpy
import pyautogui
import time
from PIL import Image


ZONE = 'tanaris'
ADD_BAIT = False

time.sleep(5)

zone_mapping = {
    'azshara': {
        'image': 'azshara.png',
        'confidence': 0.5,
        'standard_deviations': 2,
    },
    'barrens': {
        'image': 'barrens.png',
        'confidence': 0.5,
        'standard_deviations': 3,
    },
    'moonglade': {
        'image': 'moonglade.png',
        'confidence': 0.5,
        'standard_deviations': 3,
    },
    'stv': {
        'image': 'stv.png',
        'confidence': 0.5,
        'standard_deviations': 2,
    },
    'tanaris': {
        'image': 'tanaris.png',
        'confidence': 0.4,
        'standard_deviations': 3.25,
    },
    'winterspring': {
        'image': 'winterspring.png',
        'confidence': 0.4,
        'standard_deviations': 2,
    },
    'eastern_plaguelands': {
        'image': 'eastern_plaguelands.png',
        'confidence': 0.5,
        'standard_deviations': 3,
    },
}

IMAGE_FILE = f'zone_images/{zone_mapping[ZONE]["image"]}'
CONFIDENCE = zone_mapping[ZONE]["confidence"]
STANDARD_DEVIATIONS = zone_mapping[ZONE]["standard_deviations"]


def reset_cursor():
    pyautogui.move(200, 200)
    print('resetting cursor')


start_fishing = datetime.utcnow()
while True:
    if ADD_BAIT and datetime.utcnow() - start_fishing > timedelta(minutes=10):
        pyautogui.press('-')
        time.sleep(10)
        start_fishing = datetime.utcnow()
        print('bait applied')

    # throw bobber
    pyautogui.press('=')
    # wait for bobber to render
    time.sleep(3)

    # take screenshot
    pyautogui.screenshot('screenshot.png')

    with Image.open('screenshot.png') as original_file:
        # get dimensions
        width, height = original_file.size
        left = width / 3
        top = height / 4
        right = (width / 3) * 2
        bottom = height / 2
        cropped_image = original_file.crop((left, top, right, bottom))
    cropped_image.save('cropped.png')

    # find the bobber
    target = pyautogui.locate(IMAGE_FILE, cropped_image, confidence=CONFIDENCE)

    if target is None:
        print('not found')
        time.sleep(2)
        continue
    print('found it')

    target_center = pyautogui.center(target)
    center_x, center_y = target_center

    # expand to full screen
    offset_center_x = center_x + left
    offset_center_y = center_y + top
    # the offset center is the center of the bobber on the full screen

    start = datetime.utcnow().timestamp()
    now = start

    monitor_images = glob.glob('monitor_bobber_*.png')
    for image in monitor_images:
        os.remove(image)
    bobber_image_averages = []

    while now < (start + 25):
        # since the offset center is the center of bobber, we want to go up and left enough to bring the
        # full bobber into the screenshot
        monitor_left = offset_center_x - 60
        monitor_top = offset_center_y - 60
        bobber = pyautogui.screenshot(f'monitor_bobber_{now}.png', region=(monitor_left, monitor_top, 200, 120))
        bobber_average = numpy.average(bobber)

        print('monitor avg', bobber_average)

        if len(bobber_image_averages) < 5:
            bobber_image_averages.append(bobber_average)
            continue

        bobbed_averages = numpy.average(bobber_image_averages)
        comparison_bobber = bobbed_averages + (STANDARD_DEVIATIONS * numpy.std(bobber_image_averages))
        print('comp bobber', comparison_bobber)

        if bobber_average > comparison_bobber:
            print('found it')
            pyautogui.rightClick(offset_center_x / 2, offset_center_y / 2)
            time.sleep(2)
            reset_cursor()
            break

        now = datetime.utcnow().timestamp()
