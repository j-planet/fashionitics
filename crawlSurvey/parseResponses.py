import json
from pprint import pprint
from dateutil.parser import parse


def parse_datetime_str(_s):
    """
    parses 'Started: Friday, November 20, 2015 1:36:41 PM' into a datetime object
    :param _s: a string
    :return: a datetime object
    """

    return parse(_s[_s.find(',') + 1:].strip())


def parse_timespent_str(_s):
    """
    parses 'Time Spent: 00:04:59' into number of seconds
    :param _s: a string
    :return: number of seconds (int)
    """

    t = _s[(_s.find(':') + 1):].strip()
    hrs, minutes, secs = t.split(':')

    return 60**2 * int(hrs) + 60 * int(minutes) + int(secs)


def strip_single_answer(_rawInput, _currentQ, _nextQ = None):
    """
    strips answer from a blob of string
    :param _rawInput: a blob q-a-q-a string
    :param _currentQ: string for the current question
    :param _nextQ: string for the next question, None if this is the last question
    :return:
    """

    startInd = _rawInput.find(_currentQ) + len(_currentQ)
    endInd = len(_rawInput) if _nextQ is None else _rawInput.find(_nextQ)

    return _rawInput[startInd : endInd].strip()


def strip_multi_answers(_rawInput, _questions):
    """
    strips a bob of questions and answers
    :param _rawInput: a blob q-a-q-a string
    :param _questions: a list of question strings
    :return: {q: a}
    """

    answers = dict()

    for currentQ, nextQ in zip(_questions, _questions[1:] + [None]):
        answers[currentQ] = strip_single_answer(_rawInput, currentQ, nextQ)

    return answers

QUESTIONS = {'Q1': 'Q1: What are your favorite brands? (Please list at least 3.)',
             'Q2': 'Q2: As part of a shopping experience and purchase decision, how important are the following to you? Multiple choices are allowed.',
             'Q3': 'Q3: Please view  and give us your opinion.',
             'Q4': 'Q4: Please view  and give us your opinion.',
             'Q5': 'Q5: About your shopping behavior... (Please fill ALL 3 boxes with numbers, 0 for never/none.)',
             'Q6': 'Q6: You purchase clothes/shoes/accessories because... (select all that apply)'}

USER_PROFILE_QUESTIONS = ['Q7: Age',
                          'Q8: What is your gender?',
                          'Q9: How much total combined money did all members of your HOUSEHOLD earn last year?',
                          'Q10: US Region',
                          'Q11: Device Types']

Q3_SUB_QUESTIONS = ['What features of this service are useful to you?',
                    'What do you NOT like about it? Or, what features are NOT useful or irrelevant to you?',
                    'What are your questions/concerns regarding this service?',
                    'How much would you pay for a service like this? (Feel free to enter any amount. Or put "I wouldn\'t use it.")']

Q4_SUB_QUESTIONS = ['What features of this service are useful to you?',
                    'What features are NOT useful or irrelevant to you?',
                    'What are your questions/concerns regarding this service?',
                    'How much would you pay for a service like this? (Feel free to enter any amount. Or put "I wouldn\'t use it.")']

Q5_SUB_QUESTIONS = ['Which 1 of the two services in the previous two questions would you use? (Please state question 3 or question 4.)',
                    'How many times a month do you shop ONLINE?',
                    'How many times a month do you shop IN STORES?']

data = json.load(open('rawResponseData.json', 'r'))  # {respondent ID: {'profile': ..., 'answers': []} }

finalOutput = dict()    # { respondentID: {} }

for responseId, d in data.iteritems():
    print '=======', responseId

    # d = data['2']
    res = dict()    # { userInfo: {}, completionStatus:..., times: {}, answers: {} }

    # ================== PARSE THE HEADER SECTION ==================

    _, _, completionStatus, _, startTimeStr, lastModTimeStr, timeSpentStr, _ \
        = d['profile'].strip().split('\n')

    res['completionStatus'] = completionStatus
    res['times'] = {'timeSpent': parse_timespent_str(timeSpentStr),
                    'startTime': str(parse_datetime_str(startTimeStr)),     # str for JSON serialization
                    'lastModTime': str(parse_datetime_str(lastModTimeStr)),
                    }

    # ================== PARSE THE ANSWERS ==================
    res['answers'] = dict()

    q12data = d['answers'][0]
    q34data = d['answers'][1]
    q56data = d['answers'][2]

    # --------- PARSE QUESTION 1 ---------
    res['answers']['Q1'] = strip_single_answer(q12data, QUESTIONS['Q1'], QUESTIONS['Q2'])

    # --------- PARSE QUESTION 2 ---------
    q2Matrix = strip_single_answer(q12data, QUESTIONS['Q2']).split('\n')
    res['answers']['Q2'] = dict(zip(q2Matrix[::2], q2Matrix[1::2]))

    # --------- PARSE QUESTION 3 ---------
    res['answers']['Q3'] = strip_multi_answers(
        strip_single_answer(q34data, QUESTIONS['Q3'], QUESTIONS['Q4']),
        Q3_SUB_QUESTIONS)

    # --------- PARSE QUESTION 4 ---------
    res['answers']['Q4'] = strip_multi_answers(
        strip_single_answer(q34data, QUESTIONS['Q4']),
        Q4_SUB_QUESTIONS)

    # --------- PARSE QUESTION 5 ---------
    res['answers']['Q5'] = strip_multi_answers(
        strip_single_answer(q56data, QUESTIONS['Q5'], QUESTIONS['Q6']),
        Q5_SUB_QUESTIONS)

    # --------- PARSE QUESTION 6 ---------
    res['answers']['Q6'] = strip_single_answer(q56data, QUESTIONS['Q6']).split('\n')


    # ================== PARSE USER PROFILE ==================
    res['userInfo'] = strip_multi_answers(d['answers'][3], USER_PROFILE_QUESTIONS)

    pprint(res)

    finalOutput[responseId] = res


with open('parsedResponses.json', 'w') as fp:
    json.dump(finalOutput, fp)