'''
Created on Mar 07, 2023
@author: scanlom

yahooquery scrapes the yahoo finance web site so there are often problems. When these arise first run 
pip install yahooquery --upgrade, to see if a new version fixes the issue. If not, check
https://github.com/dpguthrie/yahooquery to see if any issues reference the problem
'''

from json import loads
from yahooquery import Ticker
from lib_log import log

class market_data_yahooquery:
    
    def __init__(self):
        pass

    def last(self, symbol):
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)
            return round(ticker.price[symbol]['regularMarketPrice'], 2)
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve last for %s" % (symbol) )
            raise err
        
class ref_data_yahooquery:
    
    def __init__(self):
        pass

    def ref_data_by_ticker(self, symbol):
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)
            summary = ticker.summary_profile
            quote = ticker.price
            return {
                'description': quote[symbol]['longName'],
                'sector': summary[symbol]['sector'],
                'industry': summary[symbol]['industry'],
            }
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve product for %s" % (symbol) )
            raise err

class financials_yahooquery:
    
    def __init__(self):
        pass

    flip_sign = [
        #Income
        'costRevenue',
        'operatingExpenses',
        'researchDev',
        'sellingGenAdmin',
        'deprAmor',
        'incomeTax',
        #Balance
        'treasuryStock',
    ]

    income_statement_map = {
        'symbol': 'ticker',
        'asOfDate': 'reportDate',
        'currencyCode': 'ccy',
        'BasicAverageShares': 'sharesBasic',
        'DilutedAverageShares': 'sharesDiluted',
        #Income
        'TotalRevenue': 'revenue',
        'CostOfRevenue': 'costRevenue',
        'GrossProfit': 'grossProfit',
        'NetInterestIncome': 'interestExpNet',
        'NetIncome': 'netIncome',
        'NetIncomeCommonStockholders': 'netIncomeCommon',
        'NetIncomeContinuousOperations': 'incomeContOp',
        'OperatingExpense': 'operatingExpenses',
        'OperatingIncome': 'operatingIncome',
        'PretaxIncome': 'pretaxIncomeLoss',
        'ResearchAndDevelopment': 'researchDev',
        'SellingGeneralAndAdministration': 'sellingGenAdmin',
        'ReconciledDepreciation': 'deprAmor',
        'TaxProvision': 'incomeTax',
        'TotalUnusualItems': 'netExtrGainLoss',
    }

    balance_sheet_map = {
        'symbol': 'ticker',
        'asOfDate': 'reportDate',
        'currencyCode': 'ccy',
        'BasicAverageShares': 'sharesBasic',
        'DilutedAverageShares': 'sharesDiluted',
        #Balance
        'AccountsPayable': 'payablesAccruals',
        'AccountsReceivable': 'accNotesRecv',
        'AdditionalPaidInCapital': 'shareCapitalAdd',
        'CashCashEquivalentsAndShortTermInvestments': 'cashEquivStInvest',
        'StockholdersEquity': 'totalEquity',
        'LongTermDebt': 'ltDebt',
        'CurrentAssets': 'totalCurAssets',
        'CurrentDebt': 'stDebt',
        'CurrentLiabilities': 'totalCurLiab',
        'Inventory': 'inventories',
        'NetPPE': 'propPlantEquipNet',
        'TotalAssets': 'totalAssets',
        'TotalNonCurrentAssets': 'totalNoncurAssets',
        'TreasuryStock': 'treasuryStock',
        'RetainedEarnings': 'retainedEarnings',
        'TotalNonCurrentLiabilitiesNetMinorityInterest': 'totalNoncurLiab',
        'TotalLiabilitiesNetMinorityInterest': 'totalLiabilities',
    }

    cash_flow_map = {
        'symbol': 'ticker',
        'asOfDate': 'reportDate',
        'currencyCode': 'ccy',
        'BasicAverageShares': 'sharesBasic',
        'DilutedAverageShares': 'sharesDiluted',
        #Cashflow
        'CashDividendsPaid': 'dividendsPaid',
        'ChangeInInventory': 'chgInventories',
        'ChangeInPayable': 'chgAccPayable',
        'ChangeInReceivables': 'chgAccountsRecv',
        'ChangeInWorkingCapital': 'chgWorkingCapital',
        'ChangesInCash': 'netChgCash',
        'DepreciationAndAmortization': 'deprAmor',
        'NetCommonStockIssuance': 'cashRepurchaseEquity',
        'EffectOfExchangeRateChanges': 'effectFxRates',
        'FinancingCashFlow': 'netCashFin',
        'NetIssuancePaymentsOfDebt': 'cashRepayDebt',
        'InvestingCashFlow': 'netCashInv',
        'OperatingCashFlow': 'netCashOps',
        'NetIncome': 'netIncomeStart',
    }

    def frame_to_json( self, df, force_int, col_map ):
        df = df.rename(col_map, axis='columns')
        
        df = df.drop([
            'periodType', 
            'BasicEPS',
            'DilutedEPS',
            'DilutedNIAvailtoComStockholders',
            'EBIT',
            'EBITDA',
            'InterestExpense',
            'InterestExpenseNonOperating',
            'InterestIncome',
            'InterestIncomeNonOperating',
            'NetIncomeFromContinuingAndDiscontinuedOperation',
            'NetIncomeFromContinuingOperationNetMinorityInterest',
            'NetIncomeIncludingNoncontrollingInterests',
            'NetNonOperatingInterestIncomeExpense',
            'NormalizedEBITDA',
            'NormalizedIncome',
            'OperatingRevenue',
            'OtherIncomeExpense',
            'OtherNonOperatingIncomeExpenses',
            'ReconciledCostOfRevenue',
            'TaxEffectOfUnusualItems',
            'TotalExpenses',
            'TotalOperatingIncomeAsReported',
            'TaxRateForCalcs',
            'GeneralAndAdministrativeExpense',
            'OtherOperatingExpenses',
            'TotalUnusualItemsExcludingGoodwill',
            'MinorityInterests',
            'OtherOperatingExpenses',
            'OtherSpecialCharges',
            'OtherunderPreferredStockDividend',
            'RentExpenseSupplemental',
            'SellingAndMarketingExpense',
            'SpecialIncomeCharges',
            'AccumulatedDepreciation',
            'AllowanceForDoubtfulAccountsReceivable',
            'BuildingsAndImprovements',
            'CapitalLeaseObligations',
            'CapitalStock',
            'CashAndCashEquivalents',
            'CashEquivalents',
            'CashFinancial',
            'CommonStock',
            'CommonStockEquity',
            'ConstructionInProgress',
            'CurrentCapitalLeaseObligation',
            'CurrentDebtAndCapitalLeaseObligation',
            'FinancialAssetsDesignatedasFairValueThroughProfitorLossTotal',
            'FinishedGoods',
            'Goodwill',
            'GoodwillAndOtherIntangibleAssets',
            'GrossAccountsReceivable',
            'GrossPPE',
            'InvestedCapital',
            'InvestmentProperties',
            'InvestmentinFinancialAssets',
            'LandAndImprovements',
            'LongTermCapitalLeaseObligation',
            'LongTermDebtAndCapitalLeaseObligation',
            'LongTermProvisions',
            'MachineryFurnitureEquipment',
            'MinorityInterest',
            'NetTangibleAssets',
            'NonCurrentDeferredTaxesAssets',
            'WorkingCapital',
            'TotalTaxPayable',
            'NonCurrentDeferredTaxesLiabilities',
            'NonCurrentPrepaidAssets',
            'OrdinarySharesNumber',
            'OtherCurrentLiabilities',
            'OtherEquityInterest',
            'OtherIntangibleAssets',
            'OtherPayable',
            'OtherProperties',
            'OtherReceivables',
            'OtherShortTermInvestments',
            'Payables',
            'PensionandOtherPostRetirementBenefitPlansCurrent',
            'PrepaidAssets',
            'Properties',
            'ShareIssued',
            'TangibleBookValue',
            'TaxesReceivable',
            'TotalEquityGrossMinorityInterest',
            'TotalDebt',
            'TotalCapitalization',
            'BeginningCashPosition',
            'CapitalExpenditure',
            'AmortizationCashFlow',
            'ChangeInCashSupplementalAsReported',
            'CommonStockDividendPaid',
            'CommonStockIssuance',
            'CommonStockPayments',
            'DeferredTax',
            'Depreciation',
            'DividendsReceivedCFI',
            'EffectOfExchangeRateChanges',
            'EndCashPosition',
            'FreeCashFlow',
            'GainLossOnInvestmentSecurities',
            'GainLossOnSaleOfPPE',
            'InterestPaidCFF',
            'InterestReceivedCFI',
            'IssuanceOfCapitalStock',
            'IssuanceOfDebt',
            'LongTermDebtIssuance',
            'LongTermDebtPayments',
            'NetIncomeFromContinuingOperations',
            'NetIntangiblesPurchaseAndSale',
            'NetInvestmentPropertiesPurchaseAndSale',
            'NetInvestmentPurchaseAndSale',
            'NetLongTermDebtIssuance',
            'PurchaseOfInvestmentProperties',
            'TaxesRefundPaid',
            'StockBasedCompensation',
            'ShortTermDebtPayments',
            'ShortTermDebtIssuance',
            'SaleOfPPE',
            'SaleOfInvestment',
            'RepurchaseOfCapitalStock',
            'RepaymentOfDebt',
            'PurchaseOfPPE',
            'PurchaseOfInvestment',
            'PurchaseOfIntangibles',
            'OtherNonCashItems',
            'NetShortTermDebtIssuance',
            'NetPPEPurchaseAndSale',
            'NetOtherFinancingCharges',
            'Amortization',
            'DepreciationAndAmortizationInIncomeStatement',
            'DepreciationIncomeStatement',
            'RentAndLandingFees',
            'RestructuringAndMergernAcquisition',
            'TotalOtherFinanceCost',
            'WriteOff',
            'AssetsHeldForSaleCurrent', 
            'AvailableForSaleSecurities',
            'CurrentProvisions',
            'DefinedPensionBenefit',
            'DerivativeProductLiabilities',
            'FinancialAssets',
            'FixedAssetsRevaluationReserve',
            'HedgingAssetsCurrent',
            'LongTermEquityInvestment',
            'NetDebt',
            'NonCurrentPensionAndOtherPostretirementBenefitPlans',
            'OtherInvestments',
            'RawMaterials',
            'RestrictedCash',
            'TradeandOtherPayablesNonCurrent',
            'TreasurySharesNumber',
            'ChangeInOtherCurrentAssets',
            'DividendReceivedCFO',
            'NetBusinessPurchaseAndSale',
            'NetForeignCurrencyExchangeGainLoss',
            'OtherCashAdjustmentOutsideChangeinCash',
            'PurchaseOfBusiness',
            'SaleOfBusiness',
            'SaleOfIntangibles',
            'InvestmentsAndAdvances',
            'InvestmentsinAssociatesatCost',
            'InvestmentsinSubsidiariesatCost',
            'Receivables',
            'TradingSecurities',
            'ChangeInOtherCurrentLiabilities',
            'NetOtherInvestingChanges',
            'ProvisionandWriteOffofAssets',
            'NetIncomeDiscontinuousOperations',
            'InvestmentsInOtherVenturesUnderEquityMethod',
            'OtherCurrentAssets',
            'OtherInventories',
            'OtherNonCurrentAssets',
            'OtherNonCurrentLiabilities',
            'WorkInProcess',
            'OtherCashAdjustmentInsideChangeinCash',
            'GainLossOnSaleOfBusiness',
            'InterestPaidCFO',
            'InterestReceivedCFO',
            'PensionAndEmployeeBenefitExpense',
            'InventoriesAdjustmentsAllowances',
            'InvestmentsinJointVenturesatCost',
            'CapitalExpenditureReported',
            'ChangeInAccruedExpense',
            'ChangeInPrepaidAssets',
            'NonCurrentAccruedExpenses',
            'NonCurrentDeferredRevenue',
            'DividendsPayable',
        ], axis='columns', errors='ignore')

        if force_int:
            json = loads(df.reset_index().to_json(orient='records',double_precision=0,date_format='iso'))
        else:
            json = loads(df.reset_index().to_json(orient='records',date_format='iso'))
            
        # Column rename fails for some fields (keys?) so has to be redone
        for j in json:
            if 'symbol' in j:
                j['ticker'] = j['symbol']
                j.pop('symbol', None)

        for j in json:
            j['publishDate'] = j['restatedDate'] = j['reportDate']
            j['fiscalYear'] = int( j['reportDate'][:4] )
            j['entryType'] = 'Y'

        # Drop the renamed columns and log out anything left for analysis
        df = df.drop([
            'ticker',
            'reportDate',
            'ccy',
            'sharesBasic',
            'sharesDiluted',
            #Income
            'revenue',
            'costRevenue',
            'grossProfit',
            'interestExpNet',
            'netIncome',
            'netIncomeCommon',
            'incomeContOp',
            'operatingExpenses',
            'operatingIncome',
            'pretaxIncomeLoss',
            'researchDev',
            'sellingGenAdmin',
            'deprAmor',
            'incomeTax',
            'netExtrGainLoss',
            #Balance
            'payablesAccruals',
            'accNotesRecv',
            'shareCapitalAdd',
            'cashEquivStInvest',
            'totalEquity',
            'ltDebt',
            'totalCurAssets',
            'stDebt',
            'totalCurLiab',
            'inventories',
            'propPlantEquipNet',
            'totalAssets',
            'totalNoncurAssets',
            'treasuryStock',
            'retainedEarnings',
            'totalNoncurLiab',
            'totalLiabilities',
            #Cashflow
            'dividendsPaid',
            'chgInventories',
            'chgAccPayable',
            'chgAccountsRecv',
            'chgWorkingCapital',
            'netChgCash',
            'deprAmor',
            'cashRepurchaseEquity',
            'effectFxRates',
            'netCashFin',
            'cashRepayDebt',
            'netCashInv',
            'netCashOps',
            'netIncomeStart',
        ], axis='columns', errors='ignore')

        if len( df.columns ) > 0:
            log.info("Unknown columns " + str( df.columns ))

        return json
    
    def financials_by_ticker(self, symbol):
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)

            json_income_statement = []
            json = self.frame_to_json( ticker.income_statement(trailing=False), True, self.income_statement_map )
            for j in json:
                if 'netIncomeCommon' not in j or j['netIncomeCommon'] is None:
                    log.info("Skipping income statement %s %d, netIncomeCommon missing" % (j['ticker'], j['fiscalYear']))
                    continue
                if 'sharesDiluted' not in j or j['sharesDiluted'] is None:
                    log.info("Skipping income statement %s %d, sharesDiluted missing" % (j['ticker'], j['fiscalYear']))
                    continue
                log.info("Adding income statement %s %d" % (j['ticker'], j['fiscalYear']))
                json_income_statement.append(j)

            json_balance_sheet = []
            json = self.frame_to_json( ticker.balance_sheet(trailing=False), True, self.balance_sheet_map )
            for j in json:
                if 'totalEquity' not in j or j['totalEquity'] is None:
                    log.info("Skipping balance sheet %s %d, totalEquity missing" % (j['ticker'], j['fiscalYear']))
                    continue
                log.info("Adding balance sheet %s %d" % (j['ticker'], j['fiscalYear']))
                json_balance_sheet.append(j)

            json_cash_flow = []
            json = self.frame_to_json( ticker.cash_flow(trailing=False), True, self.cash_flow_map )
            for j in json:
                # if 'totalEquity' not in j or j['totalEquity'] is None:
                #     log.info("Skipping balance sheet %s %d, totalEquity missing" % (j['ticker'], j['fiscalYear']))
                #     continue
                log.info("Adding cash flow %s %d" % (j['ticker'], j['fiscalYear']))
                json_cash_flow.append(j)

            # Check NetInterestIncome for sign (and other stuff)

            return json_income_statement, json_balance_sheet, json_cash_flow
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve financials for %s" % (symbol) )
            raise err

def main():
    log.info("Started...")

    # Test
    # foo  = market_data_yahooquery()
    # print( foo.last('HA') )

    test = Ticker('8074.T')
    print( test.cash_flow(trailing=True) )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 