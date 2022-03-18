#! /usr/bin/python3

import time
import argparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread
import multiprocessing
from queue import Queue


GLOBAL_GMARKET_HOME_URL = "http://global.gmarket.co.kr/Home/Main"
GLOBAL_GMARKET_REGIS_URL = (
    "https://gmemberssl.gmarket.co.kr/Registration/MemberRegistration"
)
MAILINATOR_HOME_URL = "https://www.mailinator.com"
YOPMAIL_URL = "https://yopmail.com"


def create_opt_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username")
    parser.add_argument("password", help="password")
    return parser


def create_web_driver(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def find_element_by_id_in(driver, ids):
    element = None
    for each_id in ids:
        print(each_id)
        try:
            element = driver.find_element(By.ID, each_id)
            return (element, each_id)
        except:
            pass
    return (None, "")


def remove_element(driver, element):
    driver.execute_script(
        "var element = arguments[0]; element.parentNode.removeChild(element)", element
    )


def find_element_no_except(driver, by, key):
    element = None
    try:
        element = driver.find_element(by, key)
    except:
        pass
    return element


def mailbox(driver, username):
    print("Open Mailinator")

    # Fill username
    print("Fill username")
    id_input = driver.find_element(By.ID, "addOverlay")
    id_input.clear()
    id_input.send_keys(username)

    # Click GO
    print("Move to mailbox")
    go_button = driver.find_element(By.ID, "go-to-public")
    go_button.click()

    # Succeeded ?
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "inboxpane"))
        )
    except TimeoutException:
        print("Failed to move to mailbox")
        return False

    time.sleep(1)
    print("Done opening mailbox")

    return True


def activate(driver, username):
    print("Activate Gmarket account")

    driver.get(f'https://YOPmail.com?{username}')
    # Wait for welcome email
    print("Wait for welcome email")
    # email_row = WebDriverWait(driver, 180).until(
    #     EC.presence_of_element_located(
    #         (
    #             By.PARTIAL_LINK_TEXT,
    #             "[Gmarket] Welcome new Member! Please Confirm your E-mail",
    #         )
    #     )
    # )

    # Click on the email
    # print("Open welcome email")
    # email_row.click()

    time.sleep(1)

    # # Dismiss Cookie message if any
    # cookie_got_it = find_element_no_except(driver, By.LINK_TEXT, "Got it!")
    # if cookie_got_it:
    #     print("Dismiss cookie banner")
    #     cookie_got_it.click()

    # time.sleep(1)

    # Switch to message body iframe
    print("Click on 'Verify your email address'")
    # driver.switch_to_frame("msg_body")

    # wait until "//iframe[@id='ifmail']" exists and find element
    
    # frame = driver.find_element(By.XPATH,"//iframe[@id='ifmail']")

    frame = WebDriverWait(driver, 180).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//iframe[@id='ifmail']",
            )
        )
    )

    # WebDriverWait(driver, 180).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@id='ifmail']")))
    driver.switch_to.frame(frame)

    # verify_button = WebDriverWait(driver, 180).until(EC.visibility_of_element_located((By.LINK_TEXT, "Verify your email address")))

    # verify_button = WebDriverWait(driver, 180).until(
    #         EC.presence_of_element_located((By.LINK_TEXT, "Verify your email address"))
    #     )

    verify_button = driver.find_element(By.LINK_TEXT, "Verify your email address")
    if verify_button:
        verify_button.click()
    else:
        print("Failed to find verify button")
        return False
    time.sleep(1)

    driver.switch_to.default_content()

    time.sleep(1)
    print("Done verifying email")

    return True


def coupon(driver, username, password):
    print("Receive coupon")

    # Remove Preference popup
    popup_layer = find_element_no_except(driver, By.ID, "GmktPopLayer")
    if popup_layer:
        print("Remove preference popup layer")
        remove_element(driver, popup_layer)

    time.sleep(1)

    # Switch to message body iframe
    print("Click on 'Sign In'")
    signin_button = driver.find_element(By.LINK_TEXT, "Sign In")
    signin_button.click()

    time.sleep(1)

    # Fill username
    print("Fill username")
    id_input = driver.find_element(By.ID, "id")
    id_input.clear()
    id_input.send_keys(username)

    # Fill password
    print("Fill password")
    password_input = driver.find_element(By.ID, "pwd")
    password_input.clear()
    password_input.send_keys(password)

    # Click Sign In
    print("Click on 'Sign In'")
    signin_button = driver.find_element(By.ID, "goCheckLogin")
    signin_button.click()

    time.sleep(1)

    # Remove Preference popup again
    popup_layer = find_element_no_except(driver, By.ID, "GmktPopLayer")
    if popup_layer:
        print("Remove preference popup layer")
        remove_element(driver, popup_layer)

    # Click Membership Zone
    print("Click on 'Membership Zone'")
    membership_button = driver.find_element(By.LINK_TEXT, "Membership Zone")
    membership_button.click()

    time.sleep(1)

    # Remove Preference popup again
    popup_layer = find_element_no_except(driver, By.ID, "modal_pop11_layer")
    if popup_layer:
        print("Remove preference popup layer")
        remove_element(driver, popup_layer)
    popup_layer = find_element_no_except(driver, By.CLASS_NAME, "modal_top")
    if popup_layer:
        print("Remove preference popup layer")
        remove_element(driver, popup_layer)

    # Click Download
    print("Click on 'Download'")
    download_buttons = driver.find_elements(By.CLASS_NAME, "button__download")
    download_buttons[0].click()

    time.sleep(1)
    print("Done receiving coupon")

    return True


def register(driver, username, email, password):
    print("Register Gmarket account")

    # Fill username
    print("Fill username")
    id_input = driver.find_element(By.ID, "id")
    id_input.clear()
    id_input.send_keys(username)

    # Fill email
    print("Fill email")
    email_input = driver.find_element(By.ID, "email")
    email_input.clear()
    email_input.send_keys(email)

    # Fill password
    print("Fill password")
    password_input = driver.find_element(By.ID, "pw")
    password_input.clear()
    password_input.send_keys(password)

    # Fill password confirmation
    print("Fill re-enter password")
    confirm_passwd_input = driver.find_element(By.ID, "rpw")
    confirm_passwd_input.clear()
    confirm_passwd_input.send_keys(password)

    # Check username & email availability
    print("Check username & email availability")
    checkers = driver.find_elements(By.LINK_TEXT, "Check Availability")

    for checker in checkers:
        checker.click()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID,'popLayerIframe1'))
        )
        check_popup_ok, _ = find_element_by_id_in(driver, ["okbutton", "okbtn"])

        if check_popup_ok is None:
            print("Couldn't locate OK button. Maybe username or email already exists...")
            return False
        check_popup_ok.click()
        driver.switch_to.default_content()

        time.sleep(.01)

    # Agree all terms
    print("Agree all terms")
    agree_check = driver.find_element(By.ID, "reg_check")
    agree_check.click()

    time.sleep(.1)

    # Submit
    print("Submit")
    submit_button = driver.find_element(By.ID, "btnSubmit")
    submit_button.click()

    time.sleep(.1)
    print("Done registering account")

    return True


if __name__ == "__main__":
    parser = create_opt_parser()
    args = parser.parse_args()

    username = args.username
    password = args.password
    
    cpu_count = multiprocessing.cpu_count()

    # yopmail = create_web_driver(YOPMAIL_URL)
    # gmarket_register = create_web_driver(GLOBAL_GMARKET_REGIS_URL)
    # gmarket_coupon = create_web_driver(GLOBAL_GMARKET_HOME_URL)

    list_username = [f'{username}{i:04d}' for i in range(100)]
    print(list_username)
    q = Queue()

    def get_handles_register(q, driver):
        while True:
            username = q.get()
            email = username + "@yopmail.com"

            print("Register Username: %s" % username)
            # print("Password: %s" % password)
            # print("Email: %s" % email)

            try:
                if (
                    register(driver, username, email, password)
                    # activate(driver, username)
                ):
                    print("All done")
            except Exception as ex:
                print("Exception: %s" % ex)
                
            driver.get(GLOBAL_GMARKET_REGIS_URL)
            q.task_done()

    def get_handles_activate(q, driver):
        while True:
            username = q.get()
            # username_test = f'{username}{i:04d}'
            email = username + "@yopmail.com"

            # gmarket_register = create_web_driver(GLOBAL_GMARKET_REGIS_URL)
            # yopmail = create_web_driver(f'{YOPMAIL_URL}?{username_test}')

            print("Activate Username: %s" % username)
            # print("Password: %s" % password)
            # print("Email: %s" % email)

            try:
                if (
                    # register(driver, username, email, password)
                    activate(driver, username)
                    # and coupon(gmarket_coupon, username, password)
                ):
                    print("All done")
            except Exception as ex:
                print("Exception: %s" % ex)
                
            # gmarket_register_driver.quit()
            # driver.get(YOPMAIL_URL)
            q.task_done()

    start = time.time()

    drivers = [create_web_driver(GLOBAL_GMARKET_REGIS_URL) for _ in range(cpu_count)]

    for i in range(cpu_count):
        t = Thread(target=get_handles_register, args=(q, drivers[i]))
        t.start()
    
    for name in list_username:
        q.put(name)

    q.join()

    [driver.quit() for driver in drivers]

    drivers = [create_web_driver(YOPMAIL_URL) for _ in range(cpu_count)]

    for i in range(cpu_count):
        t = Thread(target=get_handles_activate, args=(q, drivers[i]))
        t.start()
    
    for name in list_username:
        q.put(name)

    q.join()

    [driver.quit() for driver in drivers]

    end = time.time()
    print("Exec time: %f" % (end - start))

# indexing numpy array 2 conditions
# https://stackoverflow.com/questions/42287586/indexing-numpy-array-2-conditions
