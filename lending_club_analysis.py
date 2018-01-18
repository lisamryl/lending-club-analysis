### NOTE: csv files can be downloaded from https://www.lendingclub.com/info/download-data.action

import csv
import sys
from datetime import datetime

INVESTOR_FEE = 0.01
RECOVERY_FEE = 0.35
CLOSED_LOAN_STATUS = {'Fully Paid',
                      'Charged Off',
                      'Default',
                      'Does not meet the credit policy. Status:Fully Paid',
                      'Does not meet the credit policy. Status:Charged Off'}

def diff_month(d1, d2):
  """
  Given 2 dates in str format return the months between them.
  Args:
    d1 - first date, in format 'Mar-2014'
    d2 - second date, in format 'Mar-2014'
  Return:
    Number of months between the 2 dates
  """
  try:
    d1_date = datetime.strptime(d1, '%b-%Y')
    d2_date = datetime.strptime(d2, '%b-%Y')
  except ValueError:
    # if no data, give max (actual term will be used)
    return 60
  return abs((d2_date.year - d1_date.year) * 12 + d2_date.month - d1_date.month)

def get_data(filename):
  """
  Opens Loan Stats file and returns the needed data for each loan.
  Args:
    Filename
  Returns:
    Nested list of loans containing the following for each:
      Funded Amount (Investors)
      Issue Date
      Last Payment Date
      Total Payment (Investors)
      Loan Status
      Recoveries
      Term Date
  """
  print filename
  with open(filename, 'rb') as csvfile:
    csv.field_size_limit(sys.maxsize)
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    count = 0
    data = []
    loan_status_list = set()
    for line in reader:
      if count == 1:
        funded_amnt_inv_index = line.index('funded_amnt_inv')
        issue_d_index = line.index('issue_d')
        last_pymnt_d_index = line.index('last_pymnt_d')
        total_pymnt_inv_index = line.index('total_pymnt_inv')
        loan_status_index = line.index('loan_status')
        recoveries_index = line.index('recoveries')
        term_index = line.index('term')
      if count > 2:
        try:
          if line[loan_status_index] in CLOSED_LOAN_STATUS:
            data.append([line[funded_amnt_inv_index],
                      line[issue_d_index],
                      line[last_pymnt_d_index],
                      line[total_pymnt_inv_index],
                      line[loan_status_index],
                      line[recoveries_index],
                      line[term_index]])
        except IndexError:
          continue
      count += 1
  print count
  return data


def get_summary(bal_data):
  """
  Given a nested list for each loan, with the following data, return analysis
  Args:
    Nested list of loans containing the following for each:
      Index 0: Funded Amount (Investors)
      Index 1: Issue Date
      Index 2: Last Payment Date
      Index 3: Total Payment (Investors)
      Index 4: Loan Status
      Index 5: Recoveries
      Index 6: Term Date
  Returns:
    List of the following:
      Weighted annual return for closed loans
      Weighted annual return for fully paid loans
      Weighted annual return for defaulted/charged-off loans
      % of fully funded loans (of all closed loans)
  """
  # overall
  weighted_return = 0
  total_funding = 0

  # fully paid
  total_fully_paid = 0
  weighted_return_paid = 0
  total_funding_paid = 0

  # defaulted/charged-off
  total_defaulted = 0
  weighted_return_defaulted = 0
  total_funding_defaulted = 0

  # get annual return for each loan, and add to weighted totals
  for item in bal_data:
    funded_amnt, issue_d, last_pymnt_d, total_pmt, status, recoveries, term = item
    funded_amnt = float(funded_amnt)
    term = int(term[:3])
    # term = int(diff_month(issue_d, last_pymnt_d))
    total_pmt = float(total_pmt)
    recoveries = float(recoveries)
    try:
      perc_return = ( ( (1 - INVESTOR_FEE) * (total_pmt - recoveries)
                      + (1 - RECOVERY_FEE) * recoveries )
                      / funded_amnt - 1 )
      annual_return = ( (1 + perc_return ) ** ( 1/ (float(term) / 12)) - 1)
      if annual_return > 1 or annual_return < -1:
        print annual_return, item
    except:
      continue

    weighted_return += annual_return * funded_amnt
    total_funding += funded_amnt
    if status in ('Fully Paid', 'Does not meet the credit policy. Status:Fully Paid'):
      total_fully_paid += 1
      weighted_return_paid += annual_return * funded_amnt
      total_funding_paid += funded_amnt
    else:
      total_defaulted += 1
      weighted_return_defaulted += annual_return * funded_amnt
      total_funding_defaulted += funded_amnt

  weighted_return = weighted_return / total_funding
  weighted_return_paid = weighted_return_paid / total_funding_paid
  weighted_return_defaulted = weighted_return_defaulted / total_funding_defaulted
  perc_paid = float(total_fully_paid) / ( total_defaulted + total_fully_paid )

  return [weighted_return, weighted_return_paid, weighted_return_defaulted, perc_paid]


file_list = ['LoanStats3a.csv',
             'LoanStats3b.csv',
             'LoanStats3c.csv',
             'LoanStats3d.csv',
             'LoanStats_2016Q1.csv',
             'LoanStats_2016Q2.csv',
             'LoanStats_2016Q3.csv',
             'LoanStats_2016Q4.csv',
             'LoanStats_2017Q1.csv',
             'LoanStats_2017Q2.csv',
             'LoanStats_2017Q3.csv']

closed_loan_data = []

for file_name in file_list:
  bal_data = get_data(file_name)
  closed_loan_data.extend(bal_data)

wt_return, wt_return_paid, wt_return_defaulted, perc_paid = get_summary(closed_loan_data)
print wt_return, wt_return_paid, wt_return_defaulted, perc_paid
