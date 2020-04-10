'''
Created on Nov 13, 2017

@author: scanlom
'''

from json import loads
from simfin import load_income
from simfin import set_api_key
from simfin import set_data_dir
from api_blue_lion import post_simfin_income
from api_log import log

def main():
    log.info("Started...")
    
    # Set your API-key for downloading data.
    # If the API-key is 'free' then you will get the free data,
    # otherwise you will get the data you have paid for.
    # See www.simfin.com for what data is free and how to buy more.
    set_api_key('free')
    
    # Set the local directory where data-files are stored.
    # The dir will be created if it does not already exist.
    set_data_dir('~/simfin_data/')
    
    # Load the annual Income Statements for all companies in USA.
    # The data is automatically downloaded if you don't have it already.
    df = load_income(variant='annual', market='us')
        
    df = df.rename({
        'Ticker': 'ticker',
        'Report Date': 'reportDate',
        'SimFinId': 'simfinId',
        'Currency': 'ccy',
        'Fiscal Year': 'fiscalYear',
        'Fiscal Period': 'fiscalPeriod',
        'Publish Date': 'publishDate',
        'Shares (Basic)': 'sharesBasic',
        'Shares (Diluted)': 'sharesDiluted',
        'Revenue': 'revenue',
        'Cost of Revenue': 'costRevenue',
        'Gross Profit': 'grossProfit',
        'Operating Expenses': 'operatingExpenses',
        'Selling, General & Administrative': 'sellingGenAdmin',
        'Research & Development': 'researchDev',
        'Depreciation & Amortization': 'deprAmor',
        'Operating Income (Loss)': 'operatingIncome',
        'Non-Operating Income (Loss)': 'nonOperatingIncome',
        'Interest Expense, Net': 'interestExpNet',
        'Pretax Income (Loss), Adj.': 'pretaxIncomeLossAdj',
        'Abnormal Gains (Losses)': 'abnormGainLoss',
        'Pretax Income (Loss)': 'pretaxIncomeLoss',
        'Income Tax (Expense) Benefit, Net': 'incomeTax',
        'Income (Loss) from Continuing Operations': 'incomeContOp',
        'Net Extraordinary Gains (Losses)': 'netExtrGainLoss',
        'Net Income': 'netIncome',
        'Net Income (Common)': 'netIncomeCommon',
    }, axis='columns')
    
    json = loads(df.reset_index().to_json(orient='records',double_precision=0,date_format='iso'))
    for j in json:
        j['ticker'] = j['Ticker']
        j['reportDate'] = j['Report Date']
        j.pop('Ticker', None)
        j.pop('Report Date', None)
    
    num_records = 0
    for j in json:
        print(j)
        post_simfin_income(j)
        num_records += 1
        
    log.info("Inserted %d records" % (num_records))
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 