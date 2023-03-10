'''
Created on Jan 27, 2022
@author: scanlom
'''

import datetime as _datetime
import json as _json
import api_blue_lion as _abl
from interface_fundamentals import fundamentals_by_ticker
from lib_log import log

def safe_copy( df, json, name_df, name_json ):
    log.info('safe_copy from %s to %s' % (name_df, name_json))
    if name_df in df and df[ name_df ] is not None and 'raw' in df[ name_df ] and df[ name_df ]['raw'] is not None and df[ name_df ]['raw'] == df[ name_df ]['raw']:
        json[ name_json ] = int( df[ name_df ]['raw'] )

def safe_copy_two( df, json, name_df, name_df_two, name_json ):
    log.info('safe_copy_two from %s, %s to %s' % (name_df, name_df_two, name_json))
    val = 0
    save = False
    for name in [ name_df, name_df_two ]:
        if name in df and df[ name ] is not None and 'raw' in df[ name ] and df[ name ]['raw'] is not None and df[ name ]['raw'] == df[ name ]['raw']:
            val += df[ name ]['raw']
            save = True
    if save:
        json[ name_json ] = int( val )

def load_ref_data( ticker, quote ):
    if _abl.ref_data_by_symbol( ticker ) is None:
        log.info("Posting ref_data for " + ticker)
        _abl.post_ref_data( ticker, 
            quote['QuoteSummaryStore']['price']['longName'],
            quote['QuoteSummaryStore']['summaryProfile']['sector'],
            quote['QuoteSummaryStore']['summaryProfile']['industry'] 
            )

    if _abl.market_data_by_symbol( ticker ) is None:
        ref_data = _abl.ref_data_by_symbol( ticker )
        log.info("Posting market_data for " + ticker)
        _abl.post_market_data( ref_data['id'], quote['QuoteSummaryStore']['price']['regularMarketPrice']['raw'] )

def process_statements( ticker, currency, statements, simple_mappings, double_mappings, time_series_store,  time_series_mappings ):
    ret = {}
    for foo in statements:
        print(foo)
        bar = {}
        report_date = _datetime.datetime.utcfromtimestamp(foo['endDate']['raw'])
        bar['ticker'] = ticker
        bar['currency'] = currency
        bar['reportDate'] = bar['publishDate'] = bar['restatedDate'] = report_date.strftime("%Y-%m-%dT00:00:00Z")
        bar['fiscalYear'] = int( report_date.strftime("%Y") )
        bar['entryType'] = 'Y'
        for tuple in simple_mappings:
            safe_copy(foo, bar, tuple[0], tuple[1])
        for triple in double_mappings:
            safe_copy_two(foo, bar, triple[0], triple[1], triple[2])
        ret[report_date.strftime("%Y-%m-%d")] = bar

    for tuple in time_series_mappings:
        for foo in time_series_store[tuple[0]]:
            # We have to fuzzy map on the asOfDate year and month, as unfortunately it differs between the shares items and the income statement items
            # Statement information has date in the form 'endDate': 1633132800 (in this example 2021-10-02), while shares information is in the form
            # {'dataId': 29010, 'asOfDate': '2021-09-30', 'periodType': '12M', 'currencyCode': 'USD', 'reportedValue': 1816000000}
            if foo is None or foo['asOfDate'] is None:
                log.warning('Unable to process time_series_store %s, asOfDate None', tuple[0])
                continue
            log.info('Processing time_series_store %s with asOfDate %s' % (tuple[0],foo['asOfDate'][0:7]))
            for key in ret:
                if foo['asOfDate'][0:7] == key[0:7]:
                    ret[key][tuple[1]] = int( foo['reportedValue']['raw'] )
                    break
                elif foo['asOfDate'][0:4] == key[0:4]:
                    ret[key][tuple[1]] = int( foo['reportedValue']['raw'] )
                    break

    return ret

def load_statements( ticker, statements, get_statements, post_statement, delete_statement ):
    entries = get_statements(ticker)
    for foo in statements.values():
        log.info("Processing %s" % foo['reportDate'])
        skip = False
        for e in entries:
            if e['fiscalYear'] == foo['fiscalYear']:
                log.info("Collision found, type %s" % (e['entryType']))
                if 'S' == e['entryType']:
                    log.info("Skipping")
                    skip = True
                elif 'O' == e['entryType']:
                    log.info("Skipping")
                    skip = True
                else:
                    log.info("Overwriting, entryType " + e['entryType'])
                    delete_statement(e['id'])
        
        if not skip:
            log.info("Inserting")
            log.info(foo)
            post_statement(foo)

def load_income_statements( ticker, financials ):
    try:
        income_statements = process_statements(ticker, financials['QuoteSummaryStore']['earnings']['financialCurrency'],
            financials['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory'], [
                [ 'totalRevenue', 'revenue' ],
                [ 'costOfRevenue', 'costRevenue' ],
                [ 'grossProfit', 'grossProfit' ],
                [ 'sellingGeneralAdministrative', 'sellingGenAdmin' ],
                [ 'researchDevelopment', 'researchDev' ],
                [ 'operatingIncome', 'operatingIncome' ],
                [ 'interestExpense', 'interestExpNet' ],
                [ 'incomeBeforeTax', 'pretaxIncomeLoss' ],
                [ 'incomeTaxExpense', 'incomeTax' ],
                [ 'netIncomeFromContinuingOps', 'incomeContOp' ],
                [ 'netIncome', 'netIncome' ],
                [ 'netIncomeApplicableToCommonShares', 'netIncomeCommon' ],
            ], [
            ], financials['QuoteTimeSeriesStore']['timeSeries'], [
                [ 'annualBasicAverageShares', 'sharesBasic' ],
                [ 'annualDilutedAverageShares', 'sharesDiluted' ]
            ]
            )
    except Exception as err:
        with open('load_income_statements.json', 'w') as f:
            _json.dump(financials, f)
        log.error("json written to load_income_statements.json")
        raise err
    load_statements( ticker, income_statements, _abl.simfin_income_by_ticker, _abl.post_simfin_income, _abl.delete_simfin_income_by_id )

def load_balance_sheets( ticker, financials ):
    balance_sheets = process_statements(ticker, financials['QuoteSummaryStore']['earnings']['financialCurrency'],
        financials['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements'], [
            [ 'netReceivables', 'accNotesRecv' ],
            [ 'inventory', 'inventories' ],
            [ 'totalCurrentAssets', 'totalCurAssets' ],
            [ 'propertyPlantEquipment', 'propPlantEquipNet' ],
            [ 'totalAssets', 'totalAssets' ],
            [ 'accountsPayable', 'payablesAccruals' ],
            [ 'totalCurrentLiabilities', 'totalCurLiab' ],
            [ 'longTermDebt', 'ltDebt' ],
            [ 'treasuryStock', 'treasuryStock' ],
            [ 'retainedEarnings', 'retainedEarnings' ],
            [ 'totalStockholderEquity', 'totalEquity' ],
        ], [
            [ 'cash', 'shortTermInvestments', 'cashEquivStInvest' ],
            [ 'capitalSurplus', 'commonStock', 'shareCapitalAdd' ],
        ], financials['QuoteTimeSeriesStore']['timeSeries'], [
            [ 'annualBasicAverageShares', 'sharesBasic' ],
            [ 'annualDilutedAverageShares', 'sharesDiluted' ]
        ]
        )
    load_statements( ticker, balance_sheets, _abl.simfin_balance_by_ticker, _abl.post_simfin_balance, _abl.delete_simfin_balance_by_id )

def load_cashflow_statements( ticker, financials ):
    cashflow_statements = process_statements(ticker, financials['QuoteSummaryStore']['earnings']['financialCurrency'],
        financials['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements'], [
            [ 'netIncome', 'netIncomeStart' ],
            [ 'depreciation', 'deprAmor' ],
            [ 'changeToAccountReceivables', 'chgAccountsRecv' ],
            [ 'changeToInventory', 'chgInventories' ],
            [ 'totalCashFromOperatingActivities', 'netCashOps' ],
            [ 'capitalExpenditures', 'chgFixAssetsInt' ],
            [ 'investments', 'netChgLtInvest' ],
            [ 'totalCashflowsFromInvestingActivities', 'netCashInv' ],
            [ 'dividendsPaid', 'dividendsPaid' ],
            [ 'netBorrowings', 'cashRepayDebt' ],
            [ 'totalCashFromFinancingActivities', 'netCashFin' ],
            [ 'effectOfExchangeRate', 'effectFxRates' ],
            [ 'changeInCash', 'netChgCash' ],
        ], [
            [ 'issuanceOfStock', 'repurchaseOfStock', 'cashRepurchaseEquity' ]
        ], financials['QuoteTimeSeriesStore']['timeSeries'], [
            [ 'annualBasicAverageShares', 'sharesBasic' ],
            [ 'annualDilutedAverageShares', 'sharesDiluted' ]
        ]
        )
    load_statements( ticker, cashflow_statements, _abl.simfin_cashflow_by_ticker, _abl.post_simfin_cashflow, _abl.delete_simfin_cashflow_by_id )

def main():
    log.info("Started...")

    ticker = "HZNP"
    print(fundamentals_by_ticker(ticker))
    """quote = _af.get_quote(ticker)
    load_ref_data(ticker, quote)
    financials = _af.get_financials(ticker)
    load_income_statements(ticker, financials)
    load_balance_sheets(ticker, financials)
    load_cashflow_statements(ticker, financials)"""

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")