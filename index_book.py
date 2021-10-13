from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import time

import json

PATH = "/Users/newuser/chromedriver"

options = Options()
# options.headless = True
driver = webdriver.Chrome(PATH, options=options)
actions = ActionChains(driver)

book_url = 'https://quizlet.com/explanations/textbook-solutions/geometry-for-enjoyment-and-challenge-new-edition-9780866099653'
login_url = 'https://quizlet.com/goodbye'

tree = {'url': book_url}


def log(link, section):
    global tree
    try:
        chapter = str(link.split('-')[1])
        section = f'{chapter}.{section}'

        if chapter not in tree:
            tree[chapter] = {}
        if section not in tree[chapter]:
            tree[chapter][section] = [link]
        if link not in tree[chapter][section] and str(int(float(section))) == chapter:
            tree[chapter][section].append(link)
    except ValueError:
        print('failed')

def optimise_updates():
    # the purpose of this optimization is to capitalize on the fact that when the html data is pulled, the size is always the same
    # this algorithm with make changes to all of the chapters/select a new section every cycle because the speed is the same to process the html
    # this algorithm will cut down number of html parsings from per section, ultimatly leading to over 100 checks to about 100/sections per chapter (8-12)
    sections_first = driver.find_elements_by_css_selector("button[class='TextbookTableOfContentsList--link a1sd82zg i73vo82']")
    sections_second = driver.find_elements_by_css_selector("button[class='TextbookTableOfContentsList--link i73vo82']")
    groups = {}
    current_chapter = 1
    for index, i in enumerate(sections_first):
        groups[index+1] = [i]

    for i in sections_second:
        prompt = i.text
        if 'Section' in prompt:
            section = float(prompt.split(' ')[1][0:-1])
            chapter = int(section)
            if chapter in groups:
                groups[chapter].append(i)
        elif 'Page' in prompt:
            groups[current_chapter].append(i)
            current_chapter += 1
    print(groups)
    print(groups[3])
    for i in groups[3]:
        print(i.text)
    # groups is a dictionary with keys that are the chapters in the book
    # each key is responsible for a list of all the sections in its given chapter
    # this will cycle through all the values in each array starting at 0...1...2
    # a round consists of all sections at the current cycle index
    # ran 100 times to ensure all sections have been added
    order = []
    for i in range(100):
        round = []
        for key in groups:
            values = groups[key]
            if values:
                round.append(values[0])
                del groups[key][0]
        if round:
            order.append(round)
            continue
        break
    return order

def get_all_problems():
    hrefs = []

    driver.get(book_url)

    try:
        cs = driver.find_elements_by_class_name('c192jkj8')
        for i in cs:
            actions = ActionChains(driver)
            actions.move_to_element(i).perform()
            i.click()
    except:
        pass
    time.sleep(2)
    order = optimise_updates()
    for index, y in enumerate(order):
        for i in y:
            actions = ActionChains(driver)
            actions.move_to_element(i).perform()
            i.click()

        exercises = driver.find_elements_by_class_name('e1dpg9do')
        for exercise in exercises:
            html = str(exercise.get_attribute('innerHTML'))
            split = html.split()
            for i in split:
                if 'href' in i and 'https' in i:
                    quotes_one = i.find('"')
                    quotes_two = i.rfind('"')
                    link = i[quotes_one + 1: quotes_two]
                    link = link[link.rfind('/'):]
                    if link not in hrefs:
                        hrefs.append(link)
                        log(link, index+1)
    return hrefs

def login():
    driver.get(login_url)
    login = driver.find_element_by_xpath('//*[@id="TopNavigationReactTarget"]/header/div/div[2]/div[3]/button')
    login.click()
    time.sleep(0.2)
    username = driver.find_element_by_id('username')
    username.send_keys('ryguy661')
    time.sleep(0.2)
    username = driver.find_element_by_id('password')
    username.send_keys('Keyboard123!')
    time.sleep(0.2)
    submit = driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/section/div[2]/div/form/button')
    actions.move_to_element(submit).perform()
    time.sleep(0.2)
    submit.click()

def create_new_driver():
    global driver
    driver.close()
    driver.quit()
    driver = webdriver.Chrome(PATH, options=options)

if __name__ == '__main__':
    login()
    time.sleep(3)
    p = get_all_problems()
    print(len(p))

    with open('data.json', 'w') as json_file:
        json.dump(tree, json_file, indent=4)

    driver.close()
    driver.quit()
