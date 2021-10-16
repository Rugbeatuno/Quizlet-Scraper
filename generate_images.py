import cv2
import os
import json
import time
import numpy as np
from PIL import Image
from fpdf import FPDF

from index_book import driver, login, create_new_driver
filename = 'data.json'


book_url = ''
def combine_images(name):
    files = os.listdir('./')
    files = [i for i in files if '.png' in i if len(i) <= 6] # only gets the images with numbers ex: 1.png
    files = [(i, int(i.replace('.png', ''))) for i in files]
    files = sorted(files, key=lambda step: step[1])
    test = cv2.imread('0.png')
    height, width, c = test.shape

    concated = cv2.vconcat([cv2.imread(i[0]) for i in files])
    concated = cv2.cvtColor(concated, cv2.COLOR_BGR2RGB)
    cv2.putText(concated, name, (width-200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
    im = Image.fromarray(concated)
    im.save(name)

    for i in files:
        os.remove(i[0])

def get_solution(url):
    global iterations
    driver.get(url)
    reveal_all = None
    try:
        reveal_all = driver.find_element_by_xpath('//*[@id="TextbookExercisePageTarget"]/div[1]/div/main/div/div/div[1]/div[2]/div/div[2]/div/button[2]')
    except:
        pass
    try:
        reveal_all = driver.find_element_by_css_selector("button[class='AssemblyButtonBase AssemblyTextButton AssemblyTextButton--subtle AssemblyButtonBase--large AssemblyButtonBase--fullWidth']")
    except:
        pass
    if reveal_all:
        reveal_all.click()

    time.sleep(2)
    solutions = driver.find_elements_by_css_selector("div[data-testid='ExplanationsSolutionStep']")
    for index, i in enumerate(solutions):
        try:
            i.screenshot(f'{index}.png')
        except:
            print('HTML scraping bug.')
            continue

def load_json():
    global book_url

    with open(filename) as json_file:
        data = json.load(json_file)

        book_url = data['url']

        for chapter in data:
            if chapter == 'url':
                continue
            for section in data[chapter]:
                for index, url in enumerate(data[chapter][section]):
                    problem_url = book_url + url
                    name = f'{section}-{index + 1}.png'
                    get_solution(problem_url)
                    combine_images(name)


def prompt_user():
    with open(filename) as json_file:
        data = json.load(json_file)

        chapters = [i for i in data if i != 'url']
        print('  '.join(chapters))
        chapter = input('Enter chapter: ')

        sections = [i for i in data[chapter]]
        print('  '.join(sections))
        wanted_sections = input('Enter section(s), separate with spaces: ').split(' ')

        wanted_problems = []
        for sec in wanted_sections:
            print(f'Section {sec}: ')
            problems = []
            for i in data[chapter][sec]:
                if 'exercise' in i:
                    problems.append(i.split('-')[3])
                if 'review' in i:
                    problems.append(i.split('-')[4])
            print('  '.join(problems))

            wanted_problems.extend((data[chapter][sec][problems.index(i)], f'{sec}-{i}.png') for i in input('\nEnter problem(s), separate with spaces: ').split(' '))

        login()
        time.sleep(3)
        for problem in wanted_problems:
            url = data['url'] + problem[0]
            get_solution(url)
            combine_images(problem[1])

prompt_user()

driver.close()
driver.quit()

# login()
# time.sleep(3)
# load_json()
