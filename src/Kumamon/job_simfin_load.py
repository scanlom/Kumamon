'''
Created on Nov 13, 2017

@author: scanlom
'''

from datetime import datetime, timedelta
from json import loads
from os import path
from shutil import rmtree
from simfin import load_income, load_balance, load_cashflow, load_companies, load_industries, load_shareprices
from simfin import set_api_key
from simfin import set_data_dir
from api_blue_lion import simfin_income_by_ticker, post_simfin_income, simfin_balance_by_ticker, post_simfin_balance, simfin_cashflow_by_ticker, post_simfin_cashflow
from api_blue_lion import delete_simfin_income_by_id, delete_simfin_balance_by_id, delete_simfin_cashflow_by_id
from api_blue_lion import ref_data_by_symbol, post_ref_data, put_ref_data
from api_blue_lion import market_data_by_symbol, post_market_data, put_market_data
from api_blue_lion import mdh_by_ref_data_id_date, post_market_data_historical, put_market_data_historical
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

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
        #Market Data
        'Date': 'date',
        'Close': 'close',
        'Adj. Close': 'adjClose',
        #Companies
        'Company Name': 'companyName',
        'IndustryId': 'industryId',
        #Industries
        'Sector': 'sector',
        'Industry': 'industry',
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
        if 'Ticker' in j:
            j['ticker'] = j['Ticker']
            j.pop('Ticker', None)
        if 'Report Date' in j:
            j['reportDate'] = j['Report Date']
            j.pop('Report Date', None)
        if 'IndustryId' in j:
            j['industryId'] = j['IndustryId']
            j.pop('IndustryId', None)
        if 'Date' in j:
            j['date'] = j['Date']
            j.pop('Date', None)

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
        j['entryType'] = 'S'
        log.info(j)
        func_post(j)
        num_inserted += 1
        
    ret = "%s: Inserted %d records, collisions simfin: %d, override %d, manual %d" % (msg, num_inserted, num_collisions_simfin, num_collisions_override, num_collisions_manual)
    log.info(ret)
    return ret

def simfin_load_ref_data():
    log.info("Called simfin_load_ref_data...")

    df = load_companies(market='us')
    json_companies = frame_to_json(df)     
    df = load_industries()
    json_industries = frame_to_json(df)
    industries_by_id = { i['industryId'] : i for i in json_industries }
            
    num_inserted = 0
    num_updated = 0
    for c in json_companies:
        log.info("Processing %s" % (c['ticker']))
        sector = ""
        industry = ""
        if c['industryId'] in industries_by_id:
            sector = industries_by_id[c['industryId']]['sector']
            industry = industries_by_id[c['industryId']]['industry']
        cur = ref_data_by_symbol(c['ticker'])
        if cur == None:
            num_inserted += 1
            post_ref_data(c['ticker'], c['companyName'], sector, industry)
        else:
            num_updated += 1
            put_ref_data(cur['id'], cur['symbol'], cur['symbolAlphaVantage'], c['companyName'], sector, industry, cur['active'], cur['focus'])

    ret = "ref_data: Inserted %d records, Updated %d records" % (num_inserted, num_updated)
    log.info(ret)
    return ret

def simfin_load_market_data():
    log.info("Called simfin_load_market_data...")

    df = load_shareprices(variant='latest', market='us')
    json = frame_to_json(df)

    num_inserted = 0
    num_updated = 0
    num_price_to_old = 0
    num_no_ref_data = 0
    num_no_close = 0
    for j in json:
        log.info("Processing %s" % (j['ticker']))
        if j['close'] == None:
            num_no_close += 1
            log.info("No close found, skipping")
            continue
        if datetime.strptime(j['date'][:10], '%Y-%m-%d') < datetime.now() - timedelta(days=10):
            num_price_to_old += 1
            log.info("Price too old (%s), skipping" % (j['date']))
            continue
        cur = market_data_by_symbol(j['ticker'])
        if cur == None:
            ref = ref_data_by_symbol(j['ticker'])
            if ref == None:
                num_no_ref_data += 1
                log.info("No ref data found, skipping")
                continue
            num_inserted += 1
            post_market_data(ref['id'], j['close'])
        else:
            num_updated += 1
            put_market_data(cur['id'], cur['refDataId'], j['close'])

    ret = "market_data: Inserted %d records, Updated %d records, %d price to old and %d no ref data and %d no close" % (num_inserted, num_updated, num_price_to_old, num_no_ref_data, num_no_close)
    log.info(ret)
    return ret

def simfin_load_market_data_historical():
    log.info("Called simfin_load_market_data...")
    df = load_shareprices(variant='daily', market='us')
    json = frame_to_json(df)

    num_inserted = 0
    num_updated = 0
    num_no_ref_data = 0
    num_no_close = 0
    for j in json:
        log.info("Processing %s" % (j['ticker']))
        if j['close'] == None or j['adjClose'] == None:
            num_no_close += 1
            log.info("No close found, skipping")
            continue
        ref = ref_data_by_symbol(j['ticker'])
        if ref == None:
            num_no_ref_data += 1
            log.info("No ref data found, skipping")
            continue
        cur = mdh_by_ref_data_id_date(ref['id'],j['date'])
        if cur == None:
            num_inserted += 1
            post_market_data_historical(j['date'], ref['id'], j['close'], j['adjClose'])
        else:
            num_updated += 1
            put_market_data_historical(cur['id'], cur['date'], cur['refDataId'], j['close'], j['adjClose'])

    ret = "market_data_historical: Inserted %d records, Updated %d records, %d no ref data and %d no close" % (num_inserted, num_updated, num_no_ref_data, num_no_close)
    log.info(ret)
    return ret

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

    rpt = report()
    rpt.add_string( simfin_load("income", load_income, simfin_income_by_ticker, delete_simfin_income_by_id, post_simfin_income) )
    rpt.add_string( simfin_load("balance", load_balance, simfin_balance_by_ticker, delete_simfin_balance_by_id, post_simfin_balance) )
    rpt.add_string( simfin_load("cashflow", load_cashflow, simfin_cashflow_by_ticker, delete_simfin_cashflow_by_id, post_simfin_cashflow) )
    subject = 'Blue Lion - Simfin Load - Financials'
    send_mail_html_self(subject, rpt.get_html())

    rpt2 = report()
    rpt2.add_string( simfin_load_ref_data() )
    rpt2.add_string( simfin_load_market_data() )
    rpt2.add_string( simfin_load_market_data_historical() )
    subject = 'Blue Lion - Simfin Load - Market Data'
    send_mail_html_self(subject, rpt2.get_html())

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 