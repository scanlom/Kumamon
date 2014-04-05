'''
Created on Aug 3, 2013

@author: scanlom
'''

from urllib.request import urlopen
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from pandas.io.data import DataReader
from datetime import datetime
from log import log
import config

ADJUSTED_CLOSE = "Adj Close"

def last(symbol):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, 'l1')
    str = urlopen(url).read()
    str = str.decode()
    return float(str.strip().strip('"'))

def get_scalar_field(sql, cur, field):
    cur.execute(sql)
    rows = cur.fetchall()
    ret = 0.0 
    if len(rows) > 0:
        ret = rows[0][field]
    
    return ret 

def get_scalar(sql, cur):
    return get_scalar_field(sql, cur, 'value')

def round_ccy(value):
    return round(value, 2)

def round_pct(value):
    return round(value, 4)

class finances(object):

    def __init__(self):
        self.conn = psycopg2.connect( config.config_database_connect )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
    def __del__(self):
        self.cur.close()
        self.conn.close()

    def recon_cash(self):
        return round(self.get_cash_accounting() - self.get_cash_total() - self.get_cash_portfolio(), 2)
    
    def recon_budget(self):
        return round(self.get_budget_pos() - self.get_budget_neg(), 2)

    def balances_update(self, type, value):
        self.cur.execute("update balances set value=" + str(round(value,2)) + "where type=" + str(type))
        self.conn.commit()
       
    def balances_update_credit_cards(self, amexcx, capone, hsbcvisa):
        self.cur.execute("update balances set value=" + str(round(amexcx/7.76,2)) + "where type=1")
        self.cur.execute("update balances set value=" + str(capone) + "where type=2")
        self.cur.execute("update balances set value=" + str(round(hsbcvisa/7.76,2)) + "where type=4")
        self.conn.commit()

    def balances_update_bank_accounts(self, vbank, hsbc):
        self.cur.execute("update balances set value=" + str(vbank) + "where type=5")
        self.cur.execute("update balances set value=" + str(round(hsbc/7.76,2)) + "where type=3")
        self.conn.commit()
        
    def book_dividend_total(self, date, symbol, amount):
        cash = self.get_cash_total()
        cash += amount
        self.history_dividend_total(date, symbol, amount, cash)
        self.set_cash_total(cash)
        
    def book_interest(self, date, symbol, amount):
        cash = self.get_cash_total()
        cash += amount
        self.history_interest(date, symbol, amount, cash)
        self.set_cash_total(cash)
        
    def book_reinvestment_maanged(self, type, date, symbol, amount, quantity, price):
        quantity_new = quantity + self.get_symbol_quantity(symbol)
        self.history_reinvestment_managed(type, date, symbol, amount, quantity, price)
        self.set_symbol_quantity(symbol, quantity_new)
        
    def book_fx_hkd_to_usd(self, date, hkd, usd, rate):
        # Make sure cash is clean
        if self.recon_cash() != 0.0:
            raise Exception('ERROR book_fx_hkd_to_usd: cash not clean')
        
        # Determine difference with cash and set it
        amount = usd - ( round( hkd / 7.76, 2 ) )
        cash = self.get_cash_total()
        cash += amount
        self.history_fx_hkd_to_usd(date, amount, cash, hkd, usd, rate)
        self.set_cash_total(cash)
             
    def book_cash_infusion_portfolio(self, date, amount):
        portfolio_cash_final = self.get_cash_portfolio() + amount
        total_cash_final = self.get_cash_total() - amount
        portfolio_final = self.get_portfolio_balance() + amount
        x_final = self.get_latest_index_portfolio() / portfolio_final
        self.history_cash_infusion_portfolio(date, amount, total_cash_final, portfolio_cash_final, x_final)
        self.set_divisor_self(x_final)
        self.set_cash_portfolio(portfolio_cash_final)
        self.set_cash_total(total_cash_final)
        self.set_portfolio_balance(portfolio_final)
    
    def book_sell_managed(self, date, symbol, amount, quantity, price):
        managed_final = self.get_managed_balance() - amount
        xM_final = self.get_latest_index_401k() / managed_final 
        value_final = self.get_symbol_value(symbol) - amount
        self.history_sell_managed(date, symbol, amount, quantity, price, xM_final)
        self.set_divisor_401k(xM_final)
        self.set_symbol_value(symbol, value_final)
        cash_final = self.get_cash_total() + amount
        self.set_cash_total(cash_final)
        
        quantity_current = self.get_symbol_quantity(symbol)
        if quantity_current != None and quantity_current > 0:
            self.set_symbol_quantity(symbol, quantity_current - quantity)  
            
    def book_buy_portfolio(self, date, symbol, amount, quantity, price):
        quantity_final = self.get_symbol_quantity(symbol) + quantity
        cash_final = self.get_cash_portfolio() - amount;
        self.history_buy_portfolio(date, symbol, amount, quantity, price, cash_final)
        self.set_symbol_quantity(symbol, quantity_final)
        self.set_cash_portfolio(cash_final)

    def book_sell_portfolio(self, date, symbol, amount, quantity, price):
        quantity_final = self.get_symbol_quantity(symbol) - quantity
        cash_final = self.get_cash_portfolio() + amount;
        self.history_sell_portfolio(date, symbol, amount, quantity, price, cash_final)
        self.set_symbol_quantity(symbol, quantity_final)
        self.set_cash_portfolio(cash_final)

    def tie_out(self, msg):
        # Make sure cash is clean
        if self.recon_cash() != 0.0:
            raise Exception(msg + ': cash not clean')

        # Verify that currently rotc, roe, and managed tie out
        if self.compute_index_rotc() != self.get_latest_index_rotc():        
            raise Exception(msg + ': rotc index not clean')
        if self.compute_index_roe() != self.get_latest_index_roe():        
            raise Exception(msg + ': roe index not clean')
        if self.compute_index_managed() != self.get_latest_index_401k():        
            raise Exception(msg + ': managed index not clean')
        if self.compute_value_rotc() != self.get_total_capital_balance():        
            raise Exception(msg + ': rotc value not clean')
        if self.compute_value_roe() != self.get_total_equity_balance():        
            raise Exception(msg + ': roe value not clean')
        if self.compute_value_managed() != self.get_managed_balance():        
            raise Exception(msg + ': managed value not clean')
            
    def book_cash_infusion(self, date, amount):
        # Book Savings
        savings_cur = self.get_savings()
        savings_final = savings_cur + amount
        self.history_savings(date, amount, savings_final)
        self.set_savings(savings_final)
        log.info("Book Savings: " + str(savings_cur) + " + " + str(amount) + " = " + str(savings_final))
        
        # Book Cash Infusion
        total_capital_final = self.get_total_capital_balance() + amount
        xTC_final = self.get_latest_index_rotc() / total_capital_final
        total_equity_final = self.get_total_equity_balance() + amount
        xE_final = self.get_latest_index_roe() / total_equity_final
        owe_port_final = self.get_owe_port() + amount
        cash_final = self.get_cash_total() + amount
        self.history_cash_infusion(date, amount, xTC_final, xE_final)
        self.set_divisor_rotc(xTC_final)
        self.set_divisor_roe(xE_final)
        self.set_total_capital_balance(total_capital_final)
        self.set_total_equity_balance(total_equity_final)
        self.set_owe_port(owe_port_final)
        self.set_cash_total(cash_final)
        log.info("Cash Infusion")
   
    def book_equity_bonus(self, date, value, qty):
        self.tie_out("ERROR book_equity_bonus")
    
        # Book bonus to paid
        paid_cur = self.get_paid()
        paid_final = paid_cur + value
        self.history_paid(date, value, paid_final)
        self.set_paid(paid_final)
        log.info("Book bonus to paid: " + str(paid_cur) + " + " + str(value) + " = " + str(paid_final))

        # Book Savings
        savings_cur = self.get_savings()
        savings_final = savings_cur + value
        self.history_savings(date, value, savings_final)
        self.set_savings(savings_final)
        log.info("Book Savings: " + str(savings_cur) + " + " + str(value) + " = " + str(savings_final))

        # CI to managed
        total_capital_final = self.get_total_capital_balance() + value
        xTC_final = self.get_latest_index_rotc() / total_capital_final
        total_equity_final = self.get_total_equity_balance() + value
        xE_final = self.get_latest_index_roe() / total_equity_final
        managed_final = self.get_managed_balance() + value
        x_final = self.get_latest_index_401k() / managed_final
        self.history_cash_infusion_managed(date, value, xTC_final, xE_final, x_final)
        self.set_divisor_rotc(xTC_final)
        self.set_divisor_roe(xE_final)
        self.set_divisor_401k(x_final)
        self.set_total_capital_balance(total_capital_final)
        self.set_total_equity_balance(total_equity_final)
        self.set_managed_balance(managed_final)

        # Increment GS
        self.increment_gs(value, qty)
    
        self.tie_out("ERROR book_equity_bonus")
   
    def book_cash_bonus(self, date, bonus, tax):
        self.tie_out("ERROR book_cash_bonus")
        
        # Book bonus to paid
        paid_cur = self.get_paid()
        paid_final = paid_cur + bonus
        self.history_paid(date, bonus, paid_final)
        self.set_paid(paid_final)
        log.info("Book bonus to paid: " + str(paid_cur) + " + " + str(bonus) + " = " + str(paid_final))
        
        # Book tax to tax
        tax_cur = self.get_tax()
        tax_final = tax_cur + tax
        self.history_tax(date, tax, tax_final)
        self.set_tax(tax_final)
        log.info("Book tax to tax: " + str(tax_cur) + " + " + str(tax) + " = " + str(tax_final))
 
        # CI remainder (this will handle savings and owe port)
        remainder = bonus - tax       
        self.book_cash_infusion(date, remainder)
         
        self.tie_out("ERROR book_cash_bonus")
             
    def book_pay(self, date, salary, orso):
        # First some validations

        # Make sure cash is clean
        if self.recon_cash() != 0.0:
            raise Exception('ERROR book_pay noop: cash not clean')

        # Verify that currently rotc, roe, and managed tie out
        if self.compute_index_rotc() != self.get_latest_index_rotc():        
            raise Exception('ERROR book_pay noop: rotc index not clean, run Portfolio.py')
        if self.compute_index_roe() != self.get_latest_index_roe():        
            raise Exception('ERROR book_pay noop: roe index not clean, run Portfolio.py')
        if self.compute_index_managed() != self.get_latest_index_401k():        
            raise Exception('ERROR book_pay noop: managed index not clean, run Portfolio.py')
        if self.compute_value_rotc() != self.get_total_capital_balance():        
            raise Exception('ERROR book_pay noop: rotc value not clean, run Portfolio.py')
        if self.compute_value_roe() != self.get_total_equity_balance():        
            raise Exception('ERROR book_pay noop: roe value not clean, run Portfolio.py')
        if self.compute_value_managed() != self.get_managed_balance():        
            raise Exception('ERROR book_pay noop: managed value not clean, run Portfolio.py')
              
        # Book salary to paid
        paid_cur = self.get_paid()
        salary_usd = round(salary / 7.76, 2)
        paid_final = paid_cur + salary_usd
        self.history_paid(date, salary_usd, paid_final)
        self.set_paid(paid_final)
        log.info("Book salaray to paid: " + str(paid_cur) + " + " + str(salary_usd) + " = " + str(paid_final))
        
        # Book orso to paid
        paid_cur = paid_final;
        orso_usd = round(orso / 7.76, 2)
        paid_final = paid_cur + orso_usd
        self.history_paid(date, orso_usd, paid_final)
        self.set_paid(paid_final)
        log.info("Book orso to paid: " + str(paid_cur) + " + " + str(orso_usd) + " = " + str(paid_final))
        
        # Book tax to tax
        tax_cur = self.get_tax()
        tax_usd = round(salary_usd * 0.3, 2)
        tax_final = tax_cur + tax_usd
        self.history_tax(date, tax_usd, tax_final)
        self.set_tax(tax_final)
        log.info("Book tax to tax: " + str(tax_cur) + " + " + str(tax_usd) + " = " + str(tax_final))
        
        # DI tax
        total_capital_final = self.get_total_capital_balance() + tax_usd
        xTC_final = self.get_latest_index_rotc() / total_capital_final
        debt_final = self.get_debt() + tax_usd
        cash_final = self.get_cash_total() + tax_usd
        owe_port_final = self.get_owe_port() + tax_usd
        self.history_debt_infusion(date, tax_usd, cash_final, debt_final, xTC_final, owe_port_final)
        self.set_cash_total(cash_final)
        self.set_debt(debt_final)
        self.set_divisor_rotc(xTC_final)
        self.set_owe_port(owe_port_final)
        self.set_total_capital_balance(total_capital_final)
        log.info("DI tax")
        
        # Book orso to savings
        savings_cur = self.get_savings()
        savings_final = savings_cur + orso_usd
        self.history_savings(date, orso_usd, savings_final)
        self.set_savings(savings_final)
        log.info("Book orso to savings: " + str(savings_cur) + " + " + str(orso_usd) + " = " + str(savings_final))
        
        # CI orso
        total_capital_final = self.get_total_capital_balance() + orso_usd
        xTC_final = self.get_latest_index_rotc() / total_capital_final
        total_equity_final = self.get_total_equity_balance() + orso_usd
        xE_final = self.get_latest_index_roe() / total_equity_final
        managed_final = self.get_managed_balance() + orso_usd
        x_final = self.get_latest_index_401k() / managed_final
        self.history_cash_infusion_managed(date, orso_usd, xTC_final, xE_final, x_final)
        self.set_divisor_rotc(xTC_final)
        self.set_divisor_roe(xE_final)
        self.set_divisor_401k(x_final)
        self.increment_orso(orso_usd)
        self.set_total_capital_balance(total_capital_final)
        self.set_total_equity_balance(total_equity_final)
        self.set_managed_balance(managed_final)
        log.info("CI orso")

        # Make sure cash is clean
        if self.recon_cash() != 0.0:
            raise Exception('ERROR book_pay noop: cash not clean')

        # Verify that currently rotc, roe, and managed tie out
        if self.compute_index_rotc() != self.get_latest_index_rotc():        
            raise Exception('ERROR book_pay: rotc index not clean')
        if self.compute_index_roe() != self.get_latest_index_roe():        
            raise Exception('ERROR book_pay: roe index not clean')
        if self.compute_index_managed() != self.get_latest_index_401k():        
            raise Exception('ERROR book_pay: managed index not clean')
        if self.compute_value_rotc() != self.get_total_capital_balance():        
            raise Exception('ERROR book_pay: rotc value not clean')
        if self.compute_value_roe() != self.get_total_equity_balance():        
            raise Exception('ERROR book_pay: roe value not clean')
        if self.compute_value_managed() != self.get_managed_balance():        
            raise Exception('ERROR book_pay: managed value not clean')
        
    def history_dividend_portfolio(self, date, symbol, amount, cash):
        self.cur.execute("insert into history values ('" + date + "', 1, 'Div on " + symbol + " of " + str(amount) + "', " + str(amount) + ", " + str(cash) + ",0,0,0,'" + symbol + "')")
        self.conn.commit()
    
    def history_dividend_total(self, date, symbol, amount, cash):
        self.cur.execute("insert into history values ('" + date + "', 8, 'Div on " + symbol + " of " + str(amount) + "', " + str(amount) + ", " + str(cash) + ",0,0,0,'" + symbol + "')")
        self.conn.commit()
        
    def history_interest(self, date, symbol, amount, cash):
        self.cur.execute("insert into history values ('" + date + "', 2, 'Int on " + symbol + " of " + str(amount) + "', " + str(amount) + ", " + str(cash) + ",0,0,0,'" + symbol + "')")
        self.conn.commit()

    def history_reinvestment_managed(self, type, date, symbol, amount, quantity, price):
        self.cur.execute("insert into history values ('" + date + "', " + str(type) + ", 'Reinvestment on " + symbol + " of " + str(amount) + "', " + str(amount) + ", " + str(quantity) + "," + str(price) + ",0,0,'" + symbol + "')")
        self.conn.commit()
        
    def history_sell_managed(self, date, symbol, amount, quantity, price, xM):
        self.cur.execute("insert into history values ('" + date + "',15, 'Sold " + str(quantity) + " " + symbol + " @ " + str(price) + " " + str(amount) + "', " + str(amount) + ", " + str(quantity) + "," + str(price) + "," + str(xM) + ",0,'" + symbol + "')")
        self.conn.commit()
        
    def get_cash_portfolio(self):
        return get_scalar("select * from portfolio where symbol='CASH' and type=1", self.cur)
    
    def set_cash_portfolio(self, value):
        self.cur.execute("update portfolio set value=" + str(value) + " where symbol='CASH' and type=1")
        self.conn.commit()
        
    def history_salary(self, date, symbol, amount, cash):
        self.cur.execute("insert into history values ('" + date + "', 2, 'Int on " + symbol + " of " + str(amount) + "', " + str(amount) + ", " + str(cash) + ",0,0,0,'" + symbol + "')")
        self.conn.commit()
        
    def get_cash_total(self):
        return get_scalar("select * from portfolio where symbol='CASH' and type=3", self.cur)
    
    def set_cash_total(self, value):
        self.cur.execute("update portfolio set value=" + str(value) + " where symbol='CASH' and type=3")
        self.conn.commit()
        
    def get_cash_accounting(self):
        self.cur.execute("select * from balances where recon_cash=true")
        rows = self.cur.fetchall()   
    
        total = 0
        for row in rows:
            total += row['value']
        return total
    
    def get_budget_pos(self):
        self.cur.execute("select * from balances where recon_budget_pos=true")
        rows = self.cur.fetchall()   
    
        total = 0
        for row in rows:
            total += row['value']
        return total

    def get_budget_neg(self):
        self.cur.execute("select * from balances where recon_budget_neg=true")
        rows = self.cur.fetchall()   
    
        total = 0
        for row in rows:
            total += row['value']
        return total
    
    def get_paid(self):
        return get_scalar("select * from balances where type=15", self.cur)
    
    def set_paid(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=15")
        self.conn.commit()
        
    def history_paid(self, date, amount, result):
        self.cur.execute("insert into history values ('" + date + "', 3, 'Paid " + str(amount) + "', " + str(amount) + ", " + str(result) + ",0,0,0,0)")
        self.conn.commit()

    def get_tax(self):
        return get_scalar("select * from balances where type=16", self.cur)
    
    def set_tax(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=16")
        self.conn.commit()

    def history_tax(self, date, amount, result):
        self.cur.execute("insert into history values ('" + date + "', 4, 'Tax " + str(amount) + "', " + str(amount) + ", " + str(result) + ",0,0,0,0)")
        self.conn.commit()

    def get_savings(self):
        return get_scalar("select * from balances where type=17", self.cur)
    
    def set_savings(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=17")
        self.conn.commit()

    def history_savings(self, date, amount, result):
        self.cur.execute("insert into history values ('" + date + "', 5, 'Savings " + str(amount) + "', " + str(amount) + ", " + str(result) + ",0,0,0,0)")
        self.conn.commit()
    
    def get_debt(self):
        return get_scalar("select * from portfolio where symbol='DEBT' and type=3", self.cur)
    
    def set_debt(self, value):
        self.cur.execute("update portfolio set value=" + str(value) + " where symbol='DEBT' and type=3")
        self.conn.commit()
        
    def history_debt_infusion(self, date, amount, cash, debt, xTC, owe_port):
        self.cur.execute("insert into history values ('" + date + "', 6, 'Debt Infusion of " + str(amount) + "', " + str(amount) + ", " + str(cash) + "," + str(debt) + "," + str(xTC) + "," + str(owe_port) + ",0)")
        self.conn.commit()

    def history_cash_infusion_managed(self, date, amount, xTC, xE, xM):
        self.cur.execute("insert into history values ('" + date + "', 7, 'Cash Infusion of " + str(amount) + " to Managed', " + str(amount) + ", " + str(xTC) + "," + str(xE) + "," + str(xM) + ",0,0)")
        self.conn.commit()

    def history_cash_infusion_portfolio(self, date, amount, total_cash_final, portfolio_cash_final, x):
        self.cur.execute("insert into history values ('" + date + "', 10, 'Cash Infusion of " + str(amount) + " to Portfolio', " + str(amount) + ", " + str(total_cash_final) + ", " + str(portfolio_cash_final) + ", " + str(x) + ",0,0)")
        self.conn.commit()
        
    def history_cash_infusion(self, date, amount, xTC_final, xE_final):
        self.cur.execute("insert into history values ('" + date + "', 17, 'Cash Infusion of " + str(amount) + " to Total', " + str(amount) + ", " + str(xTC_final) + ", " + str(xE_final) + ",0,0,0)")
        self.conn.commit()
        
    def history_fx_hkd_to_usd(self, date, amount, cash, hkd, usd, rate):
        self.cur.execute("insert into history values ('" + date + "', 9, 'FX HKD to USD DWC of " + str(amount) + "', " + str(amount) + ", " + str(cash) + "," + str(hkd) + "," + str(usd) + "," + str(rate) + ",0)")
        self.conn.commit()
        
    def history_buy_portfolio(self, date, symbol, amount, quantity, price, cash):
        self.cur.execute("insert into history values ('" + date + "', 11, 'Bought " + str(quantity) + " " + symbol + " @ " + str(price) + " " + str(round_ccy(amount)) + "', " + str(amount) + ", " + str(quantity) + ", " + str(price) + "," + str(round_ccy(cash)) + ",0,'" + str(symbol) + "')")
        self.conn.commit()    

    def history_sell_portfolio(self, date, symbol, amount, quantity, price, cash):
        self.cur.execute("insert into history values ('" + date + "', 16, 'Sold " + str(quantity) + " " + symbol + " @ " + str(price) + " " + str(round_ccy(amount)) + "', " + str(amount) + ", " + str(quantity) + ", " + str(price) + "," + str(round_ccy(cash)) + ",0,'" + str(symbol) + "')")
        self.conn.commit()    
    
    def get_total_equity_balance(self):
        return get_scalar("select * from balances where type=12", self.cur)

    def get_total_capital_balance(self):
        return get_scalar("select * from balances where type=18", self.cur)

    def get_portfolio_balance(self):
        return get_scalar("select * from balances where type=13", self.cur)

    def get_managed_balance(self):
        return get_scalar("select * from balances where type=14", self.cur)
    
    def set_total_capital_balance(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=18")
        self.conn.commit()

    def set_total_equity_balance(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=12")
        self.conn.commit()

    def set_managed_balance(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=14")
        self.conn.commit()

    def set_portfolio_balance(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=13")
        self.conn.commit()
    
    def get_latest_index_rotc(self):
        return get_scalar("select * from index_history where type=3 and date = (select max(date) from index_history where type=3)", self.cur)

    def get_latest_index_roe(self):
        return get_scalar("select * from index_history where type=2 and date = (select max(date) from index_history where type=2)", self.cur)

    def get_latest_index_401k(self):
        return get_scalar("select * from index_history where type=4 and date = (select max(date) from index_history where type=4)", self.cur)

    def get_latest_index_portfolio(self):
        return get_scalar("select * from index_history where type=1 and date = (select max(date) from index_history where type=1)", self.cur)
    
    def get_owe_port(self):
        return get_scalar("select * from balances where type=7", self.cur)
    
    def set_owe_port(self, value):
        self.cur.execute("update balances set value=" + str(value) + " where type=7")
        self.conn.commit()
    
    def get_divisor_rotc(self):
        return get_scalar("select * from divisors where type = 3", self.cur)
    
    def set_divisor_rotc(self, value):
        self.cur.execute("update divisors set value=" + str(value) + " where type=3")
        self.conn.commit()

    def get_divisor_roe(self):
        return get_scalar("select * from divisors where type = 2", self.cur)
    
    def set_divisor_roe(self, value):
        self.cur.execute("update divisors set value=" + str(value) + " where type=2")
        self.conn.commit()

    def get_divisor_401k(self):
        return get_scalar("select * from divisors where type = 4", self.cur)
    
    def set_divisor_401k(self, value):
        self.cur.execute("update divisors set value=" + str(value) + " where type=4")
        self.conn.commit()
        
    def get_divisor_self(self):
        return get_scalar("select * from divisors where type = 1", self.cur)
    
    def set_divisor_self(self, value):
        self.cur.execute("update divisors set value=" + str(value) + " where type=1")
        self.conn.commit()
        
    def get_symbol_quantity(self, symbol):
        return get_scalar_field("select * from portfolio where symbol = '" + symbol + "'", self.cur, 'quantity')

    def get_symbol_value(self, symbol):
        return get_scalar_field("select * from portfolio where symbol = '" + symbol + "'", self.cur, 'value')

    def set_symbol_quantity(self, symbol, quantity):
        self.cur.execute("update portfolio set quantity=" + str(quantity) + " where symbol='" + symbol + "'")
        self.conn.commit()

    def set_symbol_value(self, symbol, value):
        self.cur.execute("update portfolio set value=" + str(value) + " where symbol='" + symbol + "'")
        self.conn.commit()
        
    def update_portfolio_price_value(self):
        self.cur.execute("select * from portfolio where pricing_type=1")
        rows = self.cur.fetchall()   
    
        for row in rows:
            price = round(last(row['symbol']),2)
            value = round(price * row['quantity'], 2)
            self.cur.execute("update portfolio set price=" + str(price) + ", value=" + str(value) + "where symbol = '" + row['symbol'] + "'")
            
        self.conn.commit()

    def update_stocks_price(self):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            price = round(last(row['symbol']),2)
            self.cur.execute("update stocks set price=" + str(price) + "where symbol = '" + row['symbol'] + "'")
            
        self.conn.commit()
        
    def update_stocks_historicals(self, log):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            data_symbol = symbol
            if symbol == "BRKB":
                data_symbol = "BRK-B"
            log.info( "Downloading %s..." % ( data_symbol ) )
            data = DataReader( data_symbol,  "yahoo", datetime(2000,1,1)) # Get everything back to 2000
            adjusted_close = data[ ADJUSTED_CLOSE ]
            count = len( adjusted_close )
            today = 0
            if count > 0:
                today = adjusted_close[ count - 1 ]
                
            # Day Change
            change = 0
            if count > 1:
                change = round_pct( today / adjusted_close[ count - 2 ] - 1 )
            self.cur.execute("update stocks set day_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Week Change
            change = 0
            if count > 5:
                change = round_pct( today / adjusted_close[ count - 6 ] - 1 )
            self.cur.execute("update stocks set week_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Month Change
            change = 0
            if count > 22:
                change = round_pct( today / adjusted_close[ count - 23 ] - 1 )
            self.cur.execute("update stocks set month_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Three Month Change
            change = 0
            if count > 66:
                change = round_pct( today / adjusted_close[ count - 67 ] - 1 )
            self.cur.execute("update stocks set three_month_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Year Change
            change = 0
            if count > 252:
                change = round_pct( today / adjusted_close[ count - 253 ] - 1 )
            self.cur.execute("update stocks set year_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Five Year Change
            change = 0
            if count > 1260:
                change = round_pct( ( today / adjusted_close[ count - 1261 ] ) ** ( .2 ) - 1 )
            self.cur.execute("update stocks set five_year_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Ten Year Change
            change = 0
            if count > 2520:
                change = round_pct( ( today / adjusted_close[ count - 2521 ] ) ** ( .1 ) - 1 )
            self.cur.execute("update stocks set ten_year_change=" + str(change) + "where symbol = '" + symbol + "'")
            
        self.conn.commit()
    
    def compute_value_self(self):
        sql = "select * from portfolio where type=1 and pricing_type=1";
        self.cur.execute(sql)
        rows = self.cur.fetchall()   
        
        total_self = 0
        for row in rows:
            total_self += row['value']

        sql = "select * from portfolio where type=1 and symbol='CASH'";
        total_self += get_scalar(sql, self.cur)
        return round_ccy(total_self)
    
    def compute_index_self(self):
        return round_ccy(self.compute_value_self() * self.get_divisor_self())

    def compute_value_managed(self):
        sql = "select * from portfolio where type=2 and pricing_type=1";
        self.cur.execute(sql)
        rows = self.cur.fetchall()   
        
        total_managed = 0
        for row in rows:
            total_managed += row['value']

        sql = "select * from portfolio where type=2 and pricing_type=2";
        self.cur.execute(sql)
        rows = self.cur.fetchall()   
    
        for row in rows:
            total_managed += row['value']

        return round_ccy(total_managed)
    
    def compute_index_managed(self):
        return round_ccy(self.compute_value_managed() * self.get_divisor_401k())
        
    def compute_value_roe(self):
        return round_ccy(self.compute_value_self() + self.compute_value_managed() + self.get_cash_total() - self.get_debt())  
    
    def compute_index_roe(self):
        return round_ccy(self.compute_value_roe() * self.get_divisor_roe())
        
    def compute_value_rotc(self):
        return round_ccy(self.compute_value_roe() + self.get_debt())  
    
    def compute_index_rotc(self):
        return round_ccy(self.compute_value_rotc() * self.get_divisor_rotc())
    
    def increment_orso(self, value):
        balance = get_scalar("select * from portfolio where Symbol='Dragons'", self.cur)
        balance += value / 2
        self.cur.execute("update portfolio set value=" + str(round_ccy(balance)) + " where Symbol='Dragons'")
        balance = get_scalar("select * from portfolio where Symbol='GlBonds'", self.cur)
        balance += value / 2
        self.cur.execute("update portfolio set value=" + str(round_ccy(balance)) + " where Symbol='GlBonds'")
        self.conn.commit()
        
    def increment_gs(self, value, qty):
        symbol = "GS"
        cur = self.get_symbol_quantity(symbol)
        self.set_symbol_quantity(symbol, cur + qty)
        cur = self.get_symbol_value(symbol)
        self.set_symbol_value(symbol, cur + value)    
        
        