__author__ = 'jj'

from prettytable import PrettyTable
from pprint import pprint
import itertools
import pandas
import numpy as np
from scipy.stats.stats import pearsonr


def computeProfitLoss(feePerVisit, disctPerVisit, numVisitsPerDay, numHrsPerDay, rentPerDay, salaryPerHr, logstCostPerWknd):
    """
    feePerVisit = 10            # flat fee per visit ($)
    disctPerVisit = 10          # average money made from clothes' discount per visit ($)

    numVisitsPerDay = 5         # number of visits in a day
    numHrsPerDay = 8            # number of hours per day

    rentPerDay = 225            # rent per day ($)
    salaryPerHr = 25            # stylist's salary per hour ($)

    logstCostPerWknd = 50       # logistic cost per weekend ($): cost involved in getting items to and from warehouse, per weekend (2 days)

    :return: revenue, cost, profit or loss
    """

    revenue = (feePerVisit + disctPerVisit) * numVisitsPerDay
    cost = rentPerDay + salaryPerHr * numHrsPerDay + logstCostPerWknd/2.
    plPerDay = revenue - cost
    plPerHr = plPerDay / numHrsPerDay

    return revenue, cost, plPerDay, plPerHr


# ------ input -------
feePerVisitVec = [10, 20, 30]            # flat fee per visit ($)
disctPerVisitVec = [5, 10, 15]          # average money made from clothes' discount per visit ($)

numVisitsPerDayVec = [5, 10, 15, 20, 25, 30, 35]         # number of visits in a day
numHrsPerDayVec = [4, 5, 6, 7, 8, 9, 10]           # number of hours per day

rentPerDayVec = [50, 75, 100, 150, 175]   # rent per day ($)
salaryPerHrVec = [18, 20, 22, 25, 27, 30]           # stylist's salary per hour ($)

logstCostPerWkndVec = [30, 40, 50, 60, 80]          # logistic cost per weekend ($)


# ------ output -------

header = ['Fee / V', 'Petty Cash / V', '# Visits', '# Hrs', '# V/Hr', 'Rent', 'Salary / Hr', 'log cost / Wknd',
          'REVENUE / Day', 'COST / Day', 'PROFIT / Day', 'PROFIT / Hr']
rawData = []

outputFile = open('pl.csv', 'w')
outputFile.writelines(','.join(header))
outputFile.writelines('\n')
table = PrettyTable(header)


for feePerVisit, disctPerVisit, numVisitsPerDay, numHrsPerDay, rentPerDay, salaryPerHr, logstCostPerWknd in \
        itertools.product(feePerVisitVec, disctPerVisitVec, numVisitsPerDayVec, numHrsPerDayVec, rentPerDayVec,
                          salaryPerHrVec, logstCostPerWkndVec):

    revenue, cost, plPerDay, plPerHr = computeProfitLoss(feePerVisit, disctPerVisit, numVisitsPerDay, numHrsPerDay,
                                                         rentPerDay, salaryPerHr, logstCostPerWknd)

    row = [feePerVisit, disctPerVisit, numVisitsPerDay, numHrsPerDay, 1. * numVisitsPerDay / numHrsPerDay,
           rentPerDay, salaryPerHr, logstCostPerWknd, revenue, cost, plPerDay, plPerHr]

    rawData.append(row)

    outputFile.writelines(','.join(str(n) for n in row))
    outputFile.writelines('\n')
    table.add_row(row)

# print table

outputFile.close()

# ------- summarize -------
dataDF = pandas.DataFrame(rawData, columns = header)

for col in header:
    print col, '\t\t', pearsonr(dataDF[col], dataDF['PROFIT / Hr'])

# round number of visits per hour
dataDF['rnd # V/Hr'] = [round(x, 1) for x in dataDF['# V/Hr']]

summary = dataDF.pivot_table(index=['Fee / V', 'Petty Cash / V'], columns=['rnd # V/Hr'], values='PROFIT / Hr', aggfunc = np.mean)