from selenium import webdriver
from selenium.webdriver import ActionChains
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


# phantomjs_path = "your_path_to_phantomjs"
# driver = webdriver.PhantomJS(executable_path=phantomjs_path)

url = "https://user.qzone.qq.com/843662954/311"   # clear all mood records, replace [843662954] with your account
username = ""
password = ""
driver = webdriver.Firefox()  # requires executable geckodriver already on your $PATH
driver.maximize_window()


def stable_get_element(the_driver, by_what, the_string):
    """avoid stale element reference exception etc"""
    attempt = 1
    while True:
        try:
            time.sleep(2)
            element = the_driver.find_element(by_what, the_string)
            return element
        except (StaleElementReferenceException, NoSuchElementException):
            if attempt == 3:
                raise
            attempt += 1


def work():
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # login
    try:
        element = wait.until(
            EC.presence_of_element_located((By.ID, "login_frame")))
        driver.switch_to.frame('login_frame')
        driver.find_element_by_id('switcher_plogin').click()  # use password to log in
        driver.find_element_by_id('u').clear()
        driver.find_element_by_id('u').send_keys(username)   # username
        driver.find_element_by_id('p').clear()
        driver.find_element_by_id('p').send_keys(password)   # password
        driver.find_element_by_id('login_button').click()

        driver.switch_to.default_content()     # login_fram  -->  default_content
        element = wait.until(
            EC.presence_of_element_located((By.ID, "top_head_title")))
        print("Login Successful.")
    except TimeoutException:
        print("Login Failed.")

    driver.switch_to.default_content()
    frame = stable_get_element(driver, By.ID, "app_canvas_frame")
    driver.switch_to.frame("app_canvas_frame")
    msglist = stable_get_element(driver, By.ID, "msgList")
    msgList = driver.find_element_by_id("msgList")

    keep_going = True
    ith = 1
    while keep_going:

        if msgList.is_displayed():

            del_btn = stable_get_element(driver, By.XPATH, "//a[@class='del del_btn author_display']")
            driver.execute_script("$(arguments[0]).click();",
                                  del_btn)  # del_btn is invisible, cannot be clicked through selenium
            driver.switch_to.default_content()  # needed
            sure_btn = stable_get_element(driver, By.XPATH, '//a[@class="qz_dialog_layer_btn qz_dialog_layer_sub"]')
            ActionChains(driver).click(sure_btn).perform()
            print(ith, " Message(s) deleted.")
            ith += 1

            driver.switch_to.frame("app_canvas_frame")
            msgList = stable_get_element(driver, By.ID, "msgList")

        else:
            try:
                """it may try several times so you'll see more than one [Turn to next page now]
                while actually it'll work out"""
                next_page_btn = stable_get_element(driver, By.XPATH, "//a[contains(@id, 'pager_next')]")
                ActionChains(driver).click(next_page_btn).perform()
                print("\n------ Turn to next page now -------------\n")
            except:
                print("There's no longer next page.")
                keep_going = False

            try:
                time.sleep(10)
                msgList = stable_get_element(driver, By.ID, "msgList")
            except:
                print("Failed to get message list.")

    driver.quit()
    print("Task finished. Bye.")


if __name__ == '__main__':
    work()
