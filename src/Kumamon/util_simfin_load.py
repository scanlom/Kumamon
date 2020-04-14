'''
Created on Nov 13, 2017

@author: scanlom
'''

from json import loads
from simfin import load_income, load_balance, load_cashflow
from simfin import set_api_key
from simfin import set_data_dir
from api_blue_lion import post_simfin_income, post_simfin_balance, post_simfin_cashflow
from api_log import log

def simfin_load_cashflow():
    log.info("Called simfin_load_cashflow...")
    
    # Load the annual Cash Flow Statements for all companies in USA.
    # The data is automatically downloaded if you don't have it already.
    df = load_cashflow(variant='annual', market='us')
        
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
        'Net Income/Starting Line': 'netIncomeStart',
        'Depreciation & Amortization': 'deprAmor',
        'Non-Cash Items': 'nonCashItems',
        'Change in Working Capital': 'chgWorkingCapital',
        'Change in Accounts Receivable': 'chgAccountsRecv',
        'Change in Inventories': 'chgInventories',
        'Change in Accounts Payable': 'chgAccPayable',
        'Change in Other': 'chgOther',
        'Net Cash from Operating Activities': 'netCashOps',
        'Change in Fixed Assets & Intangibles': 'chgFixAssetsInt',
        'Net Change in Long Term Investment': 'netChgLtInvest',
        'Net Cash from Acquisitions & Divestitures': 'netCashAcqDivest',
        'Net Cash from Investing Activities': 'netCashInv',
        'Dividends Paid': 'dividendsPaid',
        'Cash from (Repayment of) Debt': 'cashRepayDebt',
        'Cash from (Repurchase of) Equity': 'cashRepurchaseEquity',
        'Net Cash from Financing Activities': 'netCashFin',
        'Net Change in Cash': 'netChgCash',
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
        post_simfin_cashflow(j)
        num_records += 1
        
    log.info("Inserted %d records" % (num_records))

def simfin_load_balance():
    log.info("Called simfin_load_balance...")
    
    # Load the annual Balance Sheets for all companies in USA.
    # The data is automatically downloaded if you don't have it already.
    df = load_balance(variant='annual', market='us')

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
        'Cash, Cash Equivalents & Short Term Investments': 'cashEquivStInvest',
        'Accounts & Notes Receivable': 'accNotesRecv',
        'Inventories': 'inventories',
        'Total Current Assets': 'totalCurAssets',
        'Property, Plant & Equipment, Net': 'propPlantEquipNet',
        'Long Term Investments & Receivables': 'ltInvestRecv',
        'Other Long Term Assets': 'otherLtAssets',
        'Total Noncurrent Assets': 'totalNoncurAssets',
        'Total Assets': 'totalAssets',
        'Payables & Accruals': 'payablesAccruals',
        'Short Term Debt': 'stDebt',
        'Total Current Liabilities': 'totalCurLiab',
        'Long Term Debt': 'ltDebt',
        'Total Noncurrent Liabilities': 'totalNoncurLiab',
        'Total Liabilities': 'totalLiabilities',
        'Share Capital & Additional Paid-In Capital': 'shareCapitalAdd',
        'Treasury Stock': 'treasuryStock',
        'Retained Earnings': 'retainedEarnings',
        'Total Equity': 'totalEquity',
        'Total Liabilities & Equity': 'totalLiabEquity',
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
        post_simfin_balance(j)
        num_records += 1
        
    log.info("Inserted %d records" % (num_records))

def simfin_load_income():
    log.info("Called simfin_load_income...")
    
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
    
    simfin_load_cashflow()
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 