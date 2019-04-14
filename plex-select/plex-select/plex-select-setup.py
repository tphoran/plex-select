#! /usr/bin/python

import boto3
import datetime
import time
import sys
from boto3.dynamodb.conditions import Key
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start_time_string = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
start_time = datetime.datetime.today()

instance_id = sys.argv[1]
owner = sys.argv[2]
relaunch = sys.argv[3]
server_title = ''
for i in range(4, len(sys.argv)):
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
# phone_number = login_info['phone_number']
phone_number = '+15712559339'


def retry_server(server_title, instance_id):
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
                'LaunchTemplateName': 'plex-select-ec2-launch-template',
                'Version': '1'},
            MaxCount=1,
            MinCount=1
                )
    ec2 = boto3.resource('ec2', region_name="us-east-1")
    ids = [instance_id]
    ec2.instances.filter(InstanceIds=ids).terminate()
    return print('Submitted and Terminated EC2')


def shutdown_server(instance_id):
    ec2 = boto3.resource('ec2', region_name="us-east-1")
    ids = [instance_id]
    ec2.instances.filter(InstanceIds=ids).terminate()
    return print('Terminated EC2')


def happy_path_setup(server_title, plex_user_name, plex_password):
    try:
        driver.get('http://127.0.0.1:32400/web/index.html')
    except Exception as ex:
        template = "Get Website: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(5)

    try:
        email_login = \
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[contains(text(), 'email')]")))
        email_login.click()
    except Exception as ex:
        template = "Login Part 1 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        email = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "email")))
        password = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "password")))
        email.send_keys(plex_user_name)
        password.send_keys(plex_password)
        sign_in = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sign in')]")))
        sign_in.click()
    except Exception as ex:
        template = "Login Part 2 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(10)

    try:
        got_it = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Got it!')]")))
        got_it.click()
    except Exception as ex:
        template = "Got It Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    if plex_user_name != 'tphoran@gmail.com':
        try:
            exit_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ModalContent-closeButton-3NY5u")))
            exit_button.click()
        except Exception as ex:
            template = "Premium Window Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            return message
        time.sleep(3)

    try:
        outside_access_toggle = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'PublishServerOnPlexOnlineKey')))
        outside_access_toggle.click()
    except Exception as ex:
        template = "Outside Access Toggle Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        server_name = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "FriendlyName")))
        server_name.clear()
        server_name.send_keys(server_title)
        next_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Next')]")))
        next_button.click()
    except Exception as ex:
        template = "Sever Name Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        add_library = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Add Library')]")))
        add_library.click()
    except Exception as ex:
        template = "Add Library Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        movies_option = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "plex-icon-movies-560")))
        movies_option.click()
    except Exception as ex:
        template = "Movies Option Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        next_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "save-btn-label-next")))
        next_button.click()
    except Exception as ex:
        template = "Next Button Part 1 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        add_folder = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "add-folder-btn")))
        add_folder.click()
    except Exception as ex:
        template = "Add Folder Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        movies_folder = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Movies")))
        movies_folder.click()
    except Exception as ex:
        template = "Movie Folder Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        add_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "add-btn")))
        add_button.click()
    except Exception as ex:
        template = "Add Button Part 1 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(5)

    try:
        add_button = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, "save-btn-label-save")))
        add_button.click()
    except Exception as ex:
        template = "Add Button Part 2 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        next_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Next')]")))
        next_button.click()
    except Exception as ex:
        template = "Next Button Part 2 Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        done_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Done')]")))
        done_button.click()
    except Exception as ex:
        template = "Done Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        setting_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "plex-icon-navbar-settings-560")))
        setting_button.click()
    except Exception as ex:
        template = "Setting Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        remote_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Remote Access')]")))
        remote_button.click()
    except Exception as ex:
        template = "Remote Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        enable_remote_access = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Enable Remote Access')]")))
        enable_remote_access.click()
    except Exception as ex:
        template = "Enable Remote Access Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(40)

    try:
        port_mapping_toggle = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.ID, 'ManualPortMappingMode')))
        port_mapping_toggle.click()
    except Exception as ex:
        template = "Port Mapping Toggle Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        retry_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Retry')]")))
        retry_button.click()
    except Exception as ex:
        template = "Retry Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(15)

    try:
        disable_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "remote-access-disable-btn")))
    except Exception as ex:
        template = "Remote Access Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message

    return 'Plex Setup!'

def clean_up_old_severs(server_title):
    try:
        setting_button = \
        WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CLASS_NAME, \
        "plex-icon-navbar-settings-560")))
        setting_button.click()
    except Exception as ex:
        template = "Setting Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        authorized_device_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Authorized Devices')]")))
        authorized_device_button.click()
    except Exception as ex:
        template = "Authorized Devices Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message

    try:
        dropdown_toggle = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dropdown-toggle')))
        dropdown_toggle.click()
    except Exception as ex:
        template = "Type Drop Down Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message

    try:
        server_selection = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Server')]")))
        server_selection.click()
    except Exception as ex:
        template = "Sever Selection Button Fail: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    time.sleep(3)

    try:
        check_names = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'name')))
        names = driver.find_elements(By.CLASS_NAME, 'name')
        remove_buttons = driver.find_elements(By.CLASS_NAME, 'remove-device-btn')
        number_to_check = 0
        while (len(names) > 1) and (len(set(names)) > 1):
            if names[number_to_check].text != server_title:
                server_name_to_remove = names[number_to_check].text
                remove_buttons[number_to_check].click()
                time.sleep(3)
                remove_button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'confirm-btn')))
                remove_button.click()
                time.sleep(3)
                yes_button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'confirm-btn')))
                yes_button.click()
                time.sleep(10)
                number_to_check = 0
                names = driver.find_elements(By.CLASS_NAME, 'name')
                remove_buttons = driver.find_elements(By.CLASS_NAME, 'remove-device-btn')
                print('eliminated sever '+ server_name_to_remove)
            else:
                print(names[number_to_check].text)
                number_to_check += 1
    except Exception as ex:
        template = "Itterative Elimination Failed: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    return 'Server Clean Up Success'

setup_outcome = happy_path_setup(server_title[:-1], user_name, password)
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('plex-logs')
end_time = datetime.datetime.today()
setup_time = round((end_time - start_time).total_seconds()/60)
data_input = {}
data_input['time'] = start_time_string
data_input['setup_time_mins'] = setup_time
data_input['owner'] = owner
data_input['relaunch'] = relaunch
data_input['server_title'] = server_title
data_input['log'] = setup_outcome
table.put_item(Item=data_input)

sns_client = boto3.client('sns', region_name="us-east-1")
sns_client.publish(PhoneNumber='+15712559339', Message=setup_outcome)

if setup_outcome == 'Plex Setup!':
    print('Plex Setup!')
    sns_client.publish(PhoneNumber=phone_number,
                       Message='Your movie, '+str(server_title)+' is ready.')
    clean_up_old_severs(server_title[:-1])
elif relaunch == 'F':
    print(setup_outcome)
    clean_up_old_severs(server_title[:-1])
    retry_server(server_title[:-1], instance_id)
elif relaunch == 'T':
    print(setup_outcome)
    sns_client.publish(PhoneNumber=phone_number,
                       Message='Your server failed to launch, please try again.')
    shutdown_server(instance_id)
