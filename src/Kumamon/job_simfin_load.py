'''
Created on Nov 13, 2017

@author: scanlom
'''

from json import loads
from os import path
from shutil import rmtree
from simfin import load_income, load_balance, load_cashflow
from simfin import set_api_key
from simfin import set_data_dir
from api_blue_lion import simfin_income_by_ticker, post_simfin_income, simfin_balance_by_ticker, post_simfin_balance, simfin_cashflow_by_ticker, post_simfin_cashflow
from api_blue_lion import delete_simfin_income_by_id, delete_simfin_balance_by_id, delete_simfin_cashflow_by_id
from api_log import log

def frame_to_json( df ):
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
        #Income
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
        #Balance
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
        #Cashflow
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
        j['entryType'] = 'S'
        j['ticker'] = j['Ticker']
        j['reportDate'] = j['Report Date']
        j.pop('Ticker', None)
        j.pop('Report Date', None)

    return json

def simfin_load(msg, func_simfin, func_get_by_ticker, func_delete_by_id, func_post):
    log.info("Called simfin_load %s..." % (msg))
    
    # Load the annual Statements for all companies in USA.
    # The data is automatically downloaded if you don't have it already.
    df = func_simfin(variant='annual', market='us')
    json = frame_to_json(df)     
 
    num_inserted = 0
    num_collisions_simfin = 0   
    num_collisions_override = 0   
    num_collisions_manual = 0   
    tickers_to_entries = {}
    for j in json:
        log.info("Processing %s, %d" % (j['ticker'],j['fiscalYear']))
        if j['ticker'] not in tickers_to_entries:
            log.info("Getting existing entries...")
            tickers_to_entries[j['ticker']] = func_get_by_ticker(j['ticker'])
        
        skip = False
        for e in tickers_to_entries[j['ticker']]:
            if e['fiscalYear'] == j['fiscalYear']:
                log.info("Collision found, type %s" % (e['entryType']))
                if 'S' == e['entryType']:
                    log.info("Skipping")
                    num_collisions_simfin += 1
                    skip = True
                elif 'O' == e['entryType']:
                    log.info("Skipping")
                    num_collisions_override += 1
                    skip = True
                else:
                    log.info("Overwriting")
                    num_collisions_manual += 1
                    func_delete_by_id(e['id'])
                
                break
        
        if skip:
            continue    
        
        log.info("Inserting")
        log.info(j)
        func_post(j)
        num_inserted += 1
        
    log.info("Inserted %d records, collisions simfin: %d, override %d, manual %d" % (num_inserted, num_collisions_simfin, num_collisions_override, num_collisions_manual))

def main():
    log.info("Started...")
    
    if path.exists( '/home/scanlom/simfin_data/' ):
        rmtree( '/home/scanlom/simfin_data/' )
    
    # Set your API-key for downloading data.
    # If the API-key is 'free' then you will get the free data,
    # otherwise you will get the data you have paid for.
    # See www.simfin.com for what data is free and how to buy more.
    set_api_key('free')
    
    # Set the local directory where data-files are stored.
    # The dir will be created if it does not already exist.
    set_data_dir('~/simfin_data/')
    
    simfin_load("income", load_income, simfin_income_by_ticker, delete_simfin_income_by_id, post_simfin_income)
    simfin_load("balance", load_balance, simfin_balance_by_ticker, delete_simfin_balance_by_id, post_simfin_balance)
    simfin_load("cashflow", load_cashflow, simfin_cashflow_by_ticker, delete_simfin_cashflow_by_id, post_simfin_cashflow)
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 