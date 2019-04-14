#! /usr/bin/python

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/home/ubuntu/miniconda3/bin/chromedriver', chrome_options=chrome_options)

driver.get('http://127.0.0.1:32400/web/index.html')
time.sleep(10)

email_login = driver.find_elements_by_xpath("//*[contains(text(), 'email')]")[0]
email_login.click()
time.sleep(1)

email = driver.find_element_by_id("email")
password = driver.find_element_by_id("password")
email.send_keys("tphoran@gmail.com")
password.send_keys("VBiLfhU9dzVQJ")

sign_in = driver.find_elements_by_xpath("//*[contains(text(), 'Sign in')]")[0]
sign_in.click()
time.sleep(10)

got_it = driver.find_elements_by_xpath("//*[contains(text(), 'Got it!')]")[0]
got_it.click()
time.sleep(30)

server_name = driver.find_element_by_id("FriendlyName")
server_name.clear()
server_name.send_keys("Monty Python")
next_button = driver.find_elements_by_xpath("//*[contains(text(), 'Next')]")[0]
next_button.click()
time.sleep(30)

add_library = driver.find_elements_by_xpath("//*[contains(text(), 'Add Library')]")[0]
add_library.click()
time.sleep(30)

movies_option = driver.find_element_by_class_name("plex-icon-movies-560")
movies_option.click()
time.sleep(10)

next_button = driver.find_element_by_class_name("save-btn-label-next")
next_button.click()
time.sleep(30)

add_folder = driver.find_element_by_class_name("add-folder-btn")
add_folder.click()
time.sleep(10)

movies_folder = driver.find_elements_by_link_text("Movies")[0]
movies_folder.click()
time.sleep(10)

add_button = driver.find_element_by_class_name("add-btn")
add_button.click()
time.sleep(10)

add_button = driver.find_element_by_class_name("save-btn-label-save")
add_button.click()
time.sleep(10)

next_button = driver.find_elements_by_xpath("//*[contains(text(), 'Next')]")[0]
next_button.click()
time.sleep(10)

done_button = driver.find_elements_by_xpath("//*[contains(text(), 'Done')]")[0]
done_button.click()
time.sleep(20)

setting_button = driver.find_element_by_class_name("plex-icon-navbar-settings-560")
setting_button.click()
time.sleep(10)

remote_button = driver.find_elements_by_xpath("//*[contains(text(), 'Remote Access')]")[0]
remote_button.click()
time.sleep(10)

port_mapping_toggle = driver.find_element_by_name('ManualPortMappingMode')
port_mapping_toggle.click()
time.sleep(10)

retry_button = driver.find_elements_by_xpath("//*[contains(text(), 'Retry')]")[0]
retry_button.click()

print('Plex Setup!')
