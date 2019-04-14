#! /usr/bin/python

import boto3
import time
import sys
from boto3.dynamodb.conditions import Key, Attr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

owner = sys.argv[1]
relaunch = sys.argv[2]
server_title = ''
for i in range(3, len(sys.argv)):
    server_title += sys.argv[i] + ' '

options = webdriver.ChromeOptions()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/home/ubuntu/miniconda3/bin/chromedriver',chrome_options=chrome_options)

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
id_table = dynamodb.Table('plex-id')
login_name = owner.lower()
login_info = id_table.query(KeyConditionExpression=Key('name').eq(login_name))['Items'][0]

user_name = login_info['user_name']
password = login_info['pw']

def retry_server(server_title):
    ec2 = boto3.client('ec2', region_name="us-east-1")
    instance = ec2.run_instances(
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': server_title

                        },
                        {
                            'Key': 'Relaunch',
                            'Value': 'T'

                        },
                        {
                            'Key': 'Owner',
                            'Value': owner

                        },
                        ]

                },
                ],
                LaunchTemplate={
                    'LaunchTemplateId': 'lt-05717a43f72369345',
                    'Version': '2'},
                    MaxCount = 1,
                    MinCount = 1
                    )
    return print('Submitted and Terminated EC2')

def happy_path_setup(server_title, plex_user_name, plex_password):
    driver.get('http://127.0.0.1:32400/web/index.html')
    time.sleep(5)

    try:
        email_login = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'email')]")))
        email_login.click()
    except:
        return 'Login Part 1 Fail'
    time.sleep(3)

    try:
        email = WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.ID, "email")))
        password = WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.ID, "password")))
        email.send_keys(plex_user_name)
        password.send_keys(plex_password)
        sign_in = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Sign in')]")))
        sign_in.click()
    except:
        return 'Login Part 2 Fail'
    time.sleep(5)

    try:
        got_it = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Got it!')]")))
        got_it.click()
    except:
        return 'Got It Fail'
    time.sleep(3)

    try:
        outside_access_toggle = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.ID, \
        'PublishServerOnPlexOnlineKey')))
        outside_access_toggle.click()
    except:
        return 'Outside Access Toggle Fail'
    time.sleep(3)

    try:
        server_name = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.ID, \
        "FriendlyName")))
        server_name.clear()
        server_name.send_keys(server_title)
        next_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Next')]")))
        next_button.click()
    except:
        return 'Sever Name Fail'
    time.sleep(3)

    try:
        add_library = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Add Library')]")))
        add_library.click()
    except:
        return 'Add Library Fail'
    time.sleep(3)

    try:
        movies_option = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "plex-icon-movies-560")))
        movies_option.click()
    except:
        return 'Movies Option Fail'
    time.sleep(3)

    try:
        next_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "save-btn-label-next")))
        next_button.click()
    except:
        return 'Next Button Part 1 Fail'
    time.sleep(3)

    try:
        add_folder = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "add-folder-btn")))
        add_folder.click()
    except:
        return 'Add Folder Fail'
    time.sleep(3)

    try:
        movies_folder = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.LINK_TEXT, \
        "Movies")))
        movies_folder.click()
    except:
        return 'Movie Folder Fail'
    time.sleep(3)

    try:
        add_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "add-btn")))
        add_button.click()
    except:
        return 'Add Button Part 1 Fail'
    time.sleep(5)

    try:
        add_button = \
        WebDriverWait(driver, 300).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "save-btn-label-save")))
        add_button.click()
    except:
        return 'Add Button Part 2 Fail'
    time.sleep(3)

    try:
        next_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Next')]")))
        next_button.click()
    except:
        return 'Next Button Part 2 Fail'
    time.sleep(3)

    try:
        done_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Done')]")))
        done_button.click()
    except:
        return 'Done Button Fail'
    time.sleep(3)

    try:
        setting_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "plex-icon-navbar-settings-560")))
        setting_button.click()
    except:
        return 'Setting Button Fail'
    time.sleep(3)

    try:
        remote_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Remote Access')]")))
        remote_button.click()
    except:
        return 'Remote Button Fail'
    time.sleep(3)

    try:
        enable_remote_access = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Enable Remote Access')]")))
        enable_remote_access.click()
    except:
        return 'Enable Remote Access Fail'
    time.sleep(30)

    try:
        port_mapping_toggle = \
        WebDriverWait(driver, 300).until(\
        EC.presence_of_element_located((By.ID, \
        'ManualPortMappingMode')))
        port_mapping_toggle.click()
    except:
        return 'Port Mapping Toggle Fail'
    time.sleep(3)

    try:
        retry_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Retry')]")))
        retry_button.click()
    except:
        return 'Retry Button Fail'

    return 'Plex Setup!'

def clean_up_old_severs(server_title):
    try:
        setting_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "plex-icon-navbar-settings-560")))
        setting_button.click()
    except:
        return 'Setting Button Fail'
    time.sleep(3)

    try:
        authorized_device_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Authorized Devices')]")))
        authorized_device_button.click()
    except:
        return 'Authorized Devices Button Fail'

    try:
        dropdown_toggle = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        'dropdown-toggle')))
        dropdown_toggle.click()
    except:
        return 'Type Drop Down Fail'

    try:
        server_selection = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.XPATH, \
        "//*[contains(text(), 'Server')]")))
        server_selection.click()
    except:
        return 'Sever Selection Button Fail'
    time.sleep(3)

    try:
        check_names = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        'name')))
        names = driver.find_elements(By.CLASS_NAME, 'name')
        remove_buttons = driver.find_elements(By.CLASS_NAME, 'remove-device-btn')
        number_to_check = 0
        while (len(names) > 1) and (len(set(names)) > 1):
            if names[number_to_check].text != server_title:
                server_name_to_remove = names[number_to_check].text
                remove_buttons[number_to_check].click()
                time.sleep(3)
                remove_button = WebDriverWait(driver, 30).until(\
                EC.presence_of_element_located((By.CLASS_NAME, \
                'confirm-btn')))
                remove_button.click()
                time.sleep(3)
                yes_button = WebDriverWait(driver, 30).until(\
                EC.presence_of_element_located((By.CLASS_NAME, \
                'confirm-btn')))
                yes_button.click()
                time.sleep(3)
                number_to_check = 0
                names = driver.find_elements(By.CLASS_NAME, 'name')
                remove_buttons = driver.find_elements(By.CLASS_NAME, 'remove-device-btn')
                print('eliminated_sever '+ server_name_to_remove)
            else:
                print(names[number_to_check].text)
                number_to_check += 1
    except:
        return 'Itterative Elimination Failed'

    return 'Server Clean Up Success'




setup_outcome = happy_path_setup(server_title[:-1], user_name, password)

if setup_outcome == 'Plex Setup!':
    print('Plex Setup!')
    clean_up_old_severs(server_title[:-1])
elif relaunch == 'F':
    print(setup_outcome)
    clean_up_old_severs(server_title[:-1])
    retry_server(server_title[:-1])
elif relaunch == 'T':
    print(setup_outcome)
