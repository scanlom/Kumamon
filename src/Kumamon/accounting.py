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

def book_equity_bonus(date, value, qty):
    db = database.finances()
    db.book_equity_bonus(date, value, qty)

def book_cash_bonus(date, bonus, tax):
    db = database.finances()
    db.book_cash_bonus(date, bonus, tax)
    
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
    '''book_cash_bonus("01/27/2014", 72873.96, 18218.56)'''
    '''book_equity_bonus("01/27/2014", 10893, 62)'''
    
    '''recon_cash()
    book_cash_infusion('03/31/2014', 2870)
    recon_cash()'''
    
    '''recon_budget()
    update_bank_accounts(2915.61, 237533.28)
    update_credit_cards(4824.60, 3284.73, 500)
    recon_budget()'''
    
    '''recon_cash()
    book_pay('03/27/2014', 120743.00, 15723.75)
    recon_cash()'''
   
    '''recon_cash()
    book_sell_managed('02/14/2014','GSMCX',56694.10,1261.551,44.94)
    recon_cash()'''
      
    '''recon_cash()
    book_sell_portfolio('12/16/2013','JNJ',32937.67,359,91.80)
    update_gs(54180.27)
    recon_cash()'''
    
    '''recon_cash()
    book_buy_portfolio('02/18/2014','MCD',25933.50,270,96.00)
    book_buy_portfolio('02/18/2014','WMT',14369.70,190,75.58)
    update_gs(20448.78)
    recon_cash()'''
    
    '''recon_cash()
    book_debt_infusion('11/30/2013',-10000.0)
    recon_cash()'''
    
    '''recon_cash()
    book_cash_infusion_portfolio('02/13/2014',124000)
    recon_cash()'''
    
    '''recon_cash()
    book_dividend_total('2013-12-30', 'GS', 20.90)
    update_gs(12888.34)
    recon_cash()'''

    '''recon_cash()
    book_fx_hkd_to_usd('02/06/2014', 490000.0, 63140.26, 7.7605)
    update_gs(77006.28)
    update_gs_hkd(0.0)
    recon_cash()'''

    '''recon_cash()
    book_dividend_portfolio('03/13/2014', 'MSFT', 322)
    #book_interest('02/28/2014','GS',1.09)
    update_gs(21326.87)
    recon_cash()'''

    '''recon_cash()
    update_owe_portfolio(11677.29)
    update_gs(99337.93)
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
    
    '''db = database.finances()
    db.set_symbol_value('Dragons', 32199.61)
    db.set_symbol_value('GlBonds', 3052.18)'''
            
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        traceback.print_exc()
        print('ERROR: %s\n', str(err))