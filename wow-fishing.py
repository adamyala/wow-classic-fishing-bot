import os
import glob
from datetime import datetime, timedelta
import numpy
import pyautogui
import time
from PIL import Image


# the zone we're fishing in
ZONE = 'tanaris'
# the number of screenshots to take of the still bobber
# these images build a standard deviation to compare again
BOBBER_SAMPLE_SIZE = 10
ADD_BAIT = False

# adding a pause after all screen interactions gives the game
# time to catch up
pyautogui.PAUSE = 2
time.sleep(5)

zone_mapping = {
    'arathi-highlands': {
        'image': 'arathi-highlands.png',
        'confidence': 0.4,
        'standard-deviations': 3,
        'open-clams': False,
    },
    'azshara': {
        'image': 'azshara.png',
        'confidence': 0.5,
        'standard-deviations': 2,
        'open-clams': True,
    },
    'barrens': {
        'image': 'barrens.png',
        'confidence': 0.5,
        'standard-deviations': 2.5,
        'open-clams': False,
    },
    'dustwallow-marsh': {
        'image': 'dustwallow-marsh.png',
        'confidence': 0.4,
        'standard-deviations': 3,
        'open-clams': False,
    },
    'eastern_plaguelands': {
        'image': 'eastern_plaguelands.png',
        'confidence': 0.5,
        'standard-deviations': 3,
        'open-clams': False,
    },
    'elwynn-forest': {
        'image': 'elwynn-forest.png',
        'confidence': 0.4,
        'standard-deviations': 3,
        'open-clams': False,
    },
    'feralas': {
        'image': 'feralas.png',
        'confidence': 0.5,
        'standard-deviations': 2,
        'open-clams': True,
    },
    'moonglade': {
        'image': 'moonglade.png',
        'confidence': 0.5,
        'standard-deviations': 2.5,
        'open-clams': False,
    },
    'redridge-mountains': {
        'image': 'redridge-mountains.png',
        'confidence': 0.4,
        'standard-deviations': 3.5,
        'open-clams': False,
    },
    'southshore': {
        'image': 'southshore.png',
        'confidence': 0.4,
        'standard-deviations': 3.25,
        'open-clams': False,
    },
    'stormwind': {
        'image': 'stormwind.png',
        'confidence': 0.4,
        'standard-deviations': 3.5,
        'open-clams': False,
    },
    'stv': {
        'image': 'stv.png',
        'confidence': 0.5,
        'standard-deviations': 3.5,
        'open-clams': False,
    },
    'tanaris': {
        'image': 'tanaris.png',
        'confidence': 0.4,
        'standard-deviations': 5.5,
        'open-clams': True,
    },
    'wetlands': {
        'image': 'wetlands.png',
        'confidence': 0.5,
        'standard-deviations': 3,
        'open-clams': False,
    },
    'winterspring': {
        'image': 'winterspring.png',
        'confidence': 0.4,
        'standard-deviations': 2,
        'open-clams': False,
    },
}

IMAGE_FILE = f'zone_images/{zone_mapping[ZONE]["image"]}'
CONFIDENCE = zone_mapping[ZONE]["confidence"]
STANDARD_DEVIATIONS = zone_mapping[ZONE]["standard-deviations"]
OPEN_CLAMS = zone_mapping[ZONE]['open-clams']


def reset_cursor():
    # puts the cursor in the upper left of the screen
    pyautogui.moveTo(200, 200)
    print('resetting cursor', datetime.now())


# different actions are performed 10 min after fishing start
# get the fishing start time so we can determine when to perform actions
print('fishing in ', ZONE)
start_fishing = datetime.utcnow()
while True:
    if datetime.utcnow() - start_fishing > timedelta(minutes=10):
        if ADD_BAIT:
            # run macro to add bait
            pyautogui.press('0')
            time.sleep(10)
            print('bait applied')
        if OPEN_CLAMS:
            # spam macro to open clams and free up inventory space
            for _ in range(10):
                pyautogui.press('-')
        start_fishing = datetime.utcnow()

    # run macro to cast bobber
    pyautogui.press('=')
    time.sleep(2)

    # take screenshot
    pyautogui.screenshot('screenshot.png')

    # the bobber most often lands in the top center of the screen
    # crop the screenshot so we can search only that area
    # faster than searching the whole screen
    with Image.open('screenshot.png') as original_file:
        # -------------
        # | | | | | | |
        # -------------
        # | | |X|X| | |
        # -------------
        # | | |X|X| | |
        # -------------
        # | | | | | | |
        # -------------
        # | | | | | | |
        # -------------
        width, height = original_file.size
        left = width / 3
        top = height / 4
        right = (width / 3) * 2
        bottom = height / 2
        cropped_image = original_file.crop((left, top, right, bottom))
    cropped_image.save('cropped.png')

    # look for the bobber. some zones work better with a different confidence level than others
    target = pyautogui.locate(IMAGE_FILE, cropped_image, confidence=CONFIDENCE)

    if target is None:
        print('not found', datetime.now())
        continue
    print('found it', datetime.now())

    target_center = pyautogui.center(target)
    center_x, center_y = target_center

    # we readd the x and y pixels that were cropped out
    offset_center_x = center_x + left
    offset_center_y = center_y + top

    # the bobber has been found and now we monitor for changes
    start = datetime.utcnow().timestamp()
    now = start

    # clean up old bobber monitoring images if they exist
    monitor_images = glob.glob('monitor_bobber_*.png')
    for image in monitor_images:
        os.remove(image)
    bobber_image_averages = []

    # the bobber floats for ~25 sec
    while now < (start + 25):
        # since the offset center is the center of bobber, we want to go up and left enough to bring the
        # full bobber into the screenshot
        monitor_left = offset_center_x - 40
        monitor_top = offset_center_y - 40
        bobber = pyautogui.screenshot(f'monitor_bobber_{now}.png', region=(monitor_left, monitor_top, 100, 100))

        # get the avg value of the monitor image
        bobber_average = numpy.average(bobber)
        print('monitor avg', bobber_average, datetime.now())

        # collect some monitor image avgs for a good baseline value
        if len(bobber_image_averages) < BOBBER_SAMPLE_SIZE:
            bobber_image_averages.append(bobber_average)
            continue

        bobbed_averages = numpy.average(bobber_image_averages)
        comparison_bobber = bobbed_averages + (STANDARD_DEVIATIONS * numpy.std(bobber_image_averages))
        print('comp bobber', comparison_bobber, datetime.now())

        if bobber_average > comparison_bobber:
            print('a bite!', datetime.now())
            pyautogui.rightClick(monitor_left + 40, monitor_top + 40)
            reset_cursor()
            break

        now = datetime.utcnow().timestamp()
