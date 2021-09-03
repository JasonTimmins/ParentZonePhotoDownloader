#!/usr/bin/env python
import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import requests

import click


@click.command()
@click.option('--email', help='Email address used to log in to ParentZone',
              prompt='Email address used to log in to ParentZone')
@click.option('--password', help='Password used to log in to ParentZone',
              prompt='Password used to log in to ParentZone')
@click.option('--output_folder', help='Output folder',
              default='./output')

def get_parentzone_photos(email, password, output_folder):
    """Downloads all photos from a ParentZone account"""
    driver = webdriver.Chrome()

    driver.get("https://www.parentzone.me/")
    driver.implicitly_wait(10)

    # Fill in email and password
    # //*[@id="email"]
    email_field = driver.find_element_by_xpath('//*[@id="email"]')
    email_field.clear()
    email_field.send_keys(email)

    # //*[@id="password"]
    passwd_field = driver.find_element_by_xpath('//*[@id="password"]')
    passwd_field.clear()
    passwd_field.send_keys(password)
    passwd_field.send_keys(Keys.RETURN)

    # Seems to work better with a pause here
    time.sleep(3)

    # Go to timeline
    driver.get('https://www.parentzone.me/gallery')

    # Seems to work better with a pause here
    time.sleep(3)

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # The page has infinite scrolling, and scrolling by the JS scroll function
    # doesn't seem to work
    # So instead, set up a loop to scroll infinitely, and stop when we
    # stop getting any more photos displaying

    # This seems to be where the gallery component is located
    html = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div/div[2]/div/div')
    lowest_image_id = sys.maxsize
    last_lowest_image_id = 0

    while True:
        # Get all photos... in the current view
        media_elements = driver.find_elements_by_tag_name('img')

        # For each image that we've found
        for element in media_elements:
            image_url = element.get_attribute('src').replace("/thumbnail", "")
            print(image_url)
            image_id = image_url[image_url.rfind("/") + 1:image_url.find("?")]
            
            # Skip images not from gallery
            if (image_url.__contains__("api.parentzone.me/v1/media")):

                if int(image_id) < lowest_image_id:
                    lowest_image_id = int(image_id)

                # Deal with file extension based on tag used to display the media
                if element.tag_name == 'img':
                    extension = 'jpg'
                elif element.tag_name == 'video':
                    extension = 'mp4'
                image_output_path = os.path.join(output_folder,
                                                    f'{image_id}.{extension}')

                # Only download and save the file if it doesn't already exist
                if not os.path.exists(image_output_path):
                    r = requests.get(image_url, allow_redirects=True)
                    open(image_output_path, 'wb').write(r.content)

        if last_lowest_image_id == lowest_image_id:
            # We've reached the bottom of the gallery so exit
            break

        last_lowest_image_id = lowest_image_id

        # Scroll
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(5)

if __name__ == '__main__':
    get_parentzone_photos()