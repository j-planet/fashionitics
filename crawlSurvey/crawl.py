# CRAWL THE RESPONSES FROM SURVEY MONKEY INTO RAW DATA

import time
import json

import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys


def wait(numSeconds):
    time.sleep(numSeconds)

browser = webdriver.Chrome()

url = 'https://www.surveymonkey.com/user/sign-in/'
titlePart = 'SurveyMonkey'

browser.get(url)
assert titlePart in browser.title

# click on "sign in with Google"
browser.find_element_by_id('hlGoogle').click()
browser.find_element_by_id('hlGoogle').click()

# ------------ get to responses page -------------

# fill in gmail address
browser.find_element_by_id('Email').send_keys('beautyofdeduction@gmail.com' + Keys.ENTER)

wait(1)

# fill in pswd
browser.find_element_by_id('Passwd').send_keys("i'mfree!!" + Keys.ENTER)

# 87 responses
browser.find_element_by_link_text('87').click()

wait(1)

# click on "individual responses"
browser.find_element_by_id('mode_tab_individual_responses').click()

wait(1)

# ------------ get the meat -------------
res = {}    # {respondent ID: {'profile': ..., 'answers': []} }

for responseId in range(87, 1, -1):

    # audience profile
    ind = 1
    profileList = browser.find_elements_by_class_name('respondent-profile')
    audienceProfile = profileList[ind].text

    assert str(responseId) in audienceProfile, 'Response Id %i not found' % responseId

    # question answers
    answersList = browser.find_elements_by_class_name('response-question-list')
    answers = [elem.text for elem in answersList[4:8]]
    assert 'Q1' in answers[0] and 'Q3' in answers[1] and 'Q5' in answers[2] and 'Q7' in answers[3], \
        'Answers were not fetched correctly.'

    res[str(responseId)] = {'profile': audienceProfile, 'answers': answers}

    print 'Finished response # %i, navigating to the previous response.' % responseId
    browser.find_element_by_css_selector('body > div.content-wrapper > div.bd.logged-in-bd > div > div.analyze-container > div > div.analyze-main-column > div.analyze-nav-content.clearfix > div.respondent-nav.sm-float-l > div > a.btn.btn-menu-left.btn-small.btn-arrow.btn-arrow-small-horiz.btn-arrow-small-left-dark.grey.no-shadow.fadeable').click()
    wait(1)

browser.quit()

with open('rawResponseData.json', 'w') as fp:
    json.dump(res, fp)