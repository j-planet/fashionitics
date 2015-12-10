import json
# from pprint import pprint
from dateutil.parser import parse
from collections import OrderedDict


def to_str(_v):
    """
    converts a given value (number of unicode) to string
    :param _v: number of unicode
    :return: string
    """

    try:
        return str(_v)
    except UnicodeEncodeError:
        return _v.encode('ascii', 'replace')


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


def extract_single_answer(_rawInput, _currentQ, _nextQ = None, _replaceNewLineCharWith=None):
    """
    strips answer from a blob of string
    :param _rawInput: a blob q-a-q-a string
    :param _currentQ: string for the current question
    :param _nextQ: string for the next question, None if this is the last question
    :param _replaceNewLineCharWith: replace newline characters from the answers with this. '>>' by default. Does not remove if None.
    :return: a string
    """

    startInd = _rawInput.find(_currentQ) + len(_currentQ)
    endInd = len(_rawInput) if _nextQ is None else _rawInput.find(_nextQ)

    res = _rawInput[startInd : endInd].strip()

    if _replaceNewLineCharWith is not None:
        res = res.replace('\n', _replaceNewLineCharWith)

    return res


def extract_multi_answers(_rawInput, _questions, _replaceNewLineCharWith=' >> '):
    """
    strips a bob of questions and answers
    :param _rawInput: a blob q-a-q-a string
    :param _questions: a list of question strings
    :param _replaceNewLineCharWith: replace newline characters from the answers with this. '>>' by default. Does not remove if None.
    :return: an OrderedDict {q: a}
    """

    answers = OrderedDict()

    for currentQ, nextQ in zip(_questions, _questions[1:] + [None]):
        answers[currentQ] = extract_single_answer(_rawInput, currentQ, nextQ, _replaceNewLineCharWith)

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

Q2_SUB_QUESTIONS = ['Being able to shop new arrivals as soon as they arrive in stores',
                    'Being able to shop sales items as soon as they are discounted',
                    'Being able to walk away with the purchase right away (for example: no delay associated with online shopping)',
                    'Fun and inspiration',
                    'Readily available celebrity-inspired outfits',
                    'Recommendations from a professional personal stylist',
                    'Saving time from: looking for garments in your size, and waiting in line for fitting rooms and cashiers',
                    'Saving the effort of hunting for things you like from many stores in the mall (i.e. \u201cWouldn\u2019t it be great if all the garments that I like are at one central location?")',
                    'Skipping the crowds at malls or boutiques',
                    'Trying a garment on in person prior to making a purchase',
                    'What else is important to you when it comes to shopping?']

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


if __name__ == '__main__':

    data = json.load(open('output/rawResponseData.json', 'r'))  # {respondent ID: {'profile': ..., 'answers': []} }

    finalOutput = dict()    # { respondentID: {} }
    outputTsvFile = open('output/parsedResponses.tsv', 'w')

    # ================== WRITE TSV HEADER ROW ==================
    outputTsvFile.write('\t'.join(
            [   'ID#',
                'completionStatus',
                'timeSpent', 'startTime', 'lastModTime']    # times
            + USER_PROFILE_QUESTIONS
            + [QUESTIONS['Q1']]                             # Q1
            + ['Q2 - ' + s for s in Q2_SUB_QUESTIONS]       # Q2
            + ['Q3 - ' + s for s in Q3_SUB_QUESTIONS]       # Q3
            + ['Q4 - ' + s for s in Q4_SUB_QUESTIONS]       # Q4
            + ['Q5 - ' + s for s in Q5_SUB_QUESTIONS]       # Q5
            + [QUESTIONS['Q6']]                             # Q6
    ) + '\n')


    for responseId, d in data.iteritems():

        print '=======', responseId

        dictEntry = dict()    # { userInfo: {}, completionStatus:..., times: {}, answers: {} }
        tsvRow = [responseId]

        # ================== PARSE THE HEADER SECTION ==================

        _, _, completionStatus, _, startTimeStr, lastModTimeStr, timeSpentStr, _ \
            = d['profile'].strip().split('\n')

        dictEntry['completionStatus'] = completionStatus
        tsvRow += [completionStatus]

        times = OrderedDict([('timeSpent', parse_timespent_str(timeSpentStr)),
                             ('startTime', str(parse_datetime_str(startTimeStr))),     # str for JSON serialization
                             ('lastModTime', str(parse_datetime_str(lastModTimeStr)))
                             ])

        dictEntry['times'] = times
        tsvRow += times.values()

        # ================== PARSE USER PROFILE ==================
        userInfo = extract_multi_answers(d['answers'][3], USER_PROFILE_QUESTIONS)

        dictEntry['userInfo'] = userInfo
        tsvRow += userInfo.values()

        # ================== PARSE THE ANSWERS ==================
        dictEntry['answers'] = dict()

        q12data = d['answers'][0]
        q34data = d['answers'][1]
        q56data = d['answers'][2]

        # --------- PARSE QUESTION 1 ---------
        q1Ans = extract_single_answer(q12data, QUESTIONS['Q1'], QUESTIONS['Q2'], _replaceNewLineCharWith=' >> ')

        dictEntry['answers']['Q1'] = q1Ans
        tsvRow += [q1Ans]


        # --------- PARSE QUESTION 2 ---------
        q2Ans = extract_multi_answers(
                extract_single_answer(q12data, QUESTIONS['Q2']),
                Q2_SUB_QUESTIONS)

        dictEntry['answers']['Q2'] = q2Ans
        tsvRow += q2Ans.values()

        # --------- PARSE QUESTION 3 ---------
        q3Ans = extract_multi_answers(
                extract_single_answer(q34data, QUESTIONS['Q3'], QUESTIONS['Q4']),
                Q3_SUB_QUESTIONS)

        dictEntry['answers']['Q3'] = q3Ans
        tsvRow += q3Ans.values()

        # --------- PARSE QUESTION 4 ---------
        q4Ans = extract_multi_answers(
                extract_single_answer(q34data, QUESTIONS['Q4']),
                Q4_SUB_QUESTIONS)

        dictEntry['answers']['Q4'] = q4Ans
        tsvRow += q4Ans.values()

        # --------- PARSE QUESTION 5 ---------
        q5Ans = extract_multi_answers(
                extract_single_answer(q56data, QUESTIONS['Q5'], QUESTIONS['Q6']),
                Q5_SUB_QUESTIONS)

        dictEntry['answers']['Q5'] = q5Ans
        tsvRow += q5Ans.values()

        # --------- PARSE QUESTION 6 ---------
        q6Ans = extract_single_answer(q56data, QUESTIONS['Q6'], _replaceNewLineCharWith=' >> ')

        dictEntry['answers']['Q6'] = q6Ans
        tsvRow += [q6Ans]

        # ================== SAVE THE RESULTS ==================
        outputTsvFile.write('\t'.join([to_str(v) for v in tsvRow]) + '\n')
        finalOutput[responseId] = dictEntry


    with open('output/parsedResponses.json', 'w') as fp:
        json.dump(finalOutput, fp)

    outputTsvFile.close()
