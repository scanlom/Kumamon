'''
Created on Aug 3, 2013

@author: scanlom
'''
import traceback, database

def update_credit_cards(amexcx, capone, hsbcvisa):
    db = database.finances()
    db.balances_update_credit_cards(amexcx, capone, hsbcvisa)
    
def update_bank_accounts(vbank, hsbc):
    db = database.finances()
    db.balances_update_bank_accounts(vbank, hsbc)

def update_ira(value):
    db = database.finances()
    db.balances_update(11, value)
    
def update_ed(value):
    db = database.finances()
    db.balances_update(8, value)
    
def update_gs(value):
    db = database.finances()
    db.balances_update(9, value)

def update_gs_hkd(value):
    db = database.finances()
    db.balances_update(10, value)

def update_owe_portfolio(value):
    db = database.finances()
    db.balances_update(7, value)
  
def book_dividend_portfolio(date, symbol, amount):
    db = database.finances()
    db.book_dividend_portfolio(date, symbol, amount)

def book_dividend_total(date, symbol, amount):
    db = database.finances()
    db.book_dividend_total(date, symbol, amount)

def book_interest(date, symbol, amount):
    db = database.finances()
    db.book_interest(date, symbol, amount)
    
def book_reinvestment_managed(type, date, symbol, amount, quantity, price):
    db = database.finances()
    db.book_reinvestment_maanged(type, date, symbol, amount, quantity, price)
    
def book_sell_managed(date, symbol, amount, quantity, price):
    db = database.finances()
    db.book_sell_managed(date, symbol, amount, quantity, price)
    
def book_pay(date, salary, orso):
    db = database.finances()
    db.book_pay(date, salary, orso)
    
def book_cash_infusion(date, amount):
    db = database.finances()
    db.book_cash_infusion(date, amount)
    
def book_fx_hkd_to_usd(date, hkd, usd, rate):
    db = database.finances()
    db.book_fx_hkd_to_usd(date, hkd, usd, rate)

def book_cash_infusion_portfolio(date, amount):
    db = database.finances()
    db.book_cash_infusion_portfolio(date, amount)
    
def book_debt_infusion(date, amount):
    db = database.finances()
    db.book_debt_infusion(date, amount)

def book_buy_portfolio(date, symbol, amount, quantity, price):
    db = database.finances()
    db.book_buy_portfolio(date, symbol, amount, quantity, price)
    
def book_sell_portfolio(date, symbol, amount, quantity, price):
    db = database.finances()
    db.book_sell_portfolio(date, symbol, amount, quantity, price)

def recon_cash():
    db = database.finances()
    print(str(db.recon_cash()))

def recon_budget():
    db = database.finances()
    print(str(db.recon_budget()))
    
def main():
    '''recon_cash()
    recon_budget()
    book_cash_infusion('12/31/2013', -17916.54)
    recon_budget()
    recon_cash()'''
    
    '''recon_budget()
    update_bank_accounts(7651.22, 136081.72)
    update_credit_cards(14459.20, 4944.54, 500)
    recon_budget()'''
    
    '''recon_cash()
    book_pay("12/24/2013", 120360.01, 15506.25)
    recon_cash()'''
    
    '''recon_cash()
    book_interest('08/30/2013','ED',0.60)
    book_interest('09/30/2013','ED',0.58)
    update_ed(1417.64)
    recon_cash()'''
    
    '''recon_cash()
    book_sell_managed('12/16/2013','GSMCX',20000.00,465.875,42.93)
    update_gs(80604.05)
    recon_cash()'''
    
    '''recon_cash()
    book_sell_portfolio('12/16/2013','JNJ',32937.67,359,91.80)
    update_gs(54180.27)
    recon_cash()'''
    
    '''recon_cash()
    book_buy_portfolio('12/20/2013','MCD',6704.60,70,95.73)
    book_buy_portfolio('12/20/2013','KO',7996.00,200,39.93)
    update_gs(12867.44)
    recon_cash()'''
    
    '''recon_cash()
    book_debt_infusion('11/30/2013',-10000.0)
    recon_cash()'''
    
    '''recon_cash()
    book_cash_infusion_portfolio('12/17/2013',26000.00)
    recon_cash()'''
    
    '''recon_cash()
    book_dividend_total('2013-12-30', 'GS', 20.90)
    update_gs(12888.34)
    recon_cash()'''

    '''recon_cash()
    book_fx_hkd_to_usd('12/16/2013', 93000.0, 11993.81, 7.754)
    update_gs(21242.60)
    update_gs_hkd(0.0)
    recon_cash()'''

    '''recon_cash()
    book_dividend_portfolio('12/16/2013', 'KO', 264.88)
    book_dividend_portfolio('12/16/2013', 'MCD', 531.36)
    update_gs(81400.29)
    recon_cash()'''

    '''recon_cash()
    update_owe_portfolio(23441.07)
    update_gs_hkd(11984.54)
    recon_cash()'''
       
    '''book_pay("07/26/2013", 117745.84, 15506.25)
    recon_cash()
    recon_budget()
    update_gs(3457.9)
    book_interest('07/31/2013','ED',0.60)
    update_ed(1416.46)
    book_dividend_portfolio('06/03/13', 'WMT', 34.78)
    update_ira(342.65)
    update_bank_accounts(17078.96, 431395.40)
    update_credit_cards(2228.60,24.14,7568)
    '''
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        traceback.print_exc()
        print('ERROR: %s\n', str(err))