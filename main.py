from datetime import datetime
import pyautogui
from PIL import Image
import time
import numpy

DEBUG = False

bobber_image_file = Image.open('zone_images/booty-bay.png')
ERROR_SENSITIVEITY = 1.4


def get_cropped_screen(left, top, right, bottom):
    image = pyautogui.screenshot()

    cropped_image = image.crop((left, top, right, bottom))

    if DEBUG:
        cropped_image.save('cropped-image.png')

    print('cropped image size', cropped_image.size)

    return cropped_image


def get_bobber_center(left, top, target):
    target_center = pyautogui.center(target)
    center_x, center_y = target_center

    # we readd the x and y pixels that were cropped out
    true_center_x = center_x + left
    true_center_y = center_y + top

    print('bobber coords', true_center_x, true_center_y)

    return true_center_x, true_center_y


def watch_bobber(x, y):
    t_end = time.time() + 20
    bobber_region = (x - 50, y - 50, 150, 150)
    initial_bobber = pyautogui.screenshot(region=bobber_region)

    if DEBUG:
        initial_bobber.save('initial-bobber.png')

    initial_array = numpy.asarray(initial_bobber)
    count = 1
    threshold = 0

    while time.time() < t_end:
        print('watch', count)

        watched_bobber = pyautogui.screenshot(region=bobber_region)

        if DEBUG:
            watched_bobber.save('watched-bobber.png')

        watched_array = numpy.asarray(watched_bobber)
        image_diff = (initial_array.astype("float") - watched_array.astype("float"))
        err = numpy.sum(image_diff ** 2)
        err /= float(initial_array.shape[0] * initial_array.shape[1])

        if not threshold:
            threshold = err * ERROR_SENSITIVEITY

        print('image_diff', err)
        count += 1

        if err > threshold:
            print('bobber moved')
            return True

    # todo: comment out
    # bobber.save('bobber.png')


def main():
    screen = pyautogui.screenshot()
    print('screen size', screen.size)
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
    left = width * (1/3)
    top = height * (1/2)
    right = width * (2/3)
    bottom = height * (3/4)

    time.sleep(3)

    while True:
        pyautogui.moveTo(200, 200)
        print('resetting cursor', datetime.now())

        # run macro to cast bobber
        pyautogui.press('=')
        print('casting bobber')
        time.sleep(2)

        cropped_image = get_cropped_screen(left, top, right, bottom)

        # look for the bobber. some zones work better with a different confidence level than others
        target = pyautogui.locate(bobber_image_file, cropped_image, confidence=.35)
        if not target:
            print('not found')
            return

        bobber_x, bobber_y = get_bobber_center(left, top, target)

        # TODO: comment out
        # pyautogui.moveTo(x=bobber_x / 2, y=bobber_y / 2)
        print('found it')

        bite = watch_bobber(bobber_x, bobber_y)
        if bite:
            pyautogui.rightClick(x=bobber_x / 2, y=bobber_y / 2)
            time.sleep(1)

main()