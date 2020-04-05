'''
Created on Aug 13, 2018

@author: scanlom
'''

from datetime import datetime
from api_log import log

CONST_CONFIDENCE_NONE           = 'NONE'
CONST_CONFIDENCE_HIGH           = 'HIGH'
CONST_CONFIDENCE_MEDIUM         = 'MEDIUM'
CONST_CONFIDENCE_LOW            = 'LOW'
CONST_CONFIDENCE_CONSTITUENT    = 'CONSTITUENT'

class report:
    CONST_FORMAT_NONE           = 0
    CONST_FORMAT_CCY            = 1
    CONST_FORMAT_CCY_COLOR      = 2
    CONST_FORMAT_CCY_INT_COLOR  = 3
    CONST_FORMAT_PCT            = 4
    CONST_FORMAT_PCT_COLOR      = 5
    CONST_FORMAT_DATE_SHORT     = 6
    CONST_FORMAT_CONFIDENCE     = 7
    
    def __init__(self):
        self.content = ""
    
    def format_ccy(self, number):
        return '{0:,.2f}'.format(number)

    def format_ccy_int(self, number):
        return '{0:,.0f}'.format(number)

    def format_pct(self, number):
        return '%{0:,.2f}'.format(100*number)
    
    def format_date_short(self, date):
        return date.strftime("%Y%m%d")
    
    def format_row(self, row, formats):
        ret = []
        for item,f in zip(row, formats):
            start = ""
            end = ""
            foo = ""
            if self.CONST_FORMAT_CCY == f or self.CONST_FORMAT_CCY_COLOR == f or self.CONST_FORMAT_CCY_INT_COLOR == f or self.CONST_FORMAT_PCT == f or self.CONST_FORMAT_PCT_COLOR == f:
                start = " style='text-align:right'"
            if self.CONST_FORMAT_CONFIDENCE == f and item == CONST_CONFIDENCE_CONSTITUENT:
                start = " bgcolor='blue'"
            start += ">"
            if self.CONST_FORMAT_CCY_COLOR == f or self.CONST_FORMAT_PCT_COLOR == f or self.CONST_FORMAT_CCY_INT_COLOR == f:
                if item > 0:
                    start += "<font color='green'>"
                else:
                    start += "<font color='red'>"
                end += "</font>"
            if self.CONST_FORMAT_NONE == f:
                foo += str(item)
            elif self.CONST_FORMAT_CCY == f or self.CONST_FORMAT_CCY_COLOR == f:
                foo += self.format_ccy(item)
            elif self.CONST_FORMAT_CCY_INT_COLOR == f:
                foo += self.format_ccy_int(item)
            elif self.CONST_FORMAT_PCT == f or self.CONST_FORMAT_PCT_COLOR == f:
                foo += self.format_pct(item)
            elif self.CONST_FORMAT_DATE_SHORT == f:
                foo += self.format_date_short(item)
            elif self.CONST_FORMAT_CONFIDENCE == f:
                foo += str(item)
                if item == CONST_CONFIDENCE_HIGH:
                    start += "<font color='green'>"
                    end += "</font>"
                elif item == CONST_CONFIDENCE_MEDIUM:
                    start += "<font color='orange'>"
                    end += "</font>"
                elif item == CONST_CONFIDENCE_CONSTITUENT:
                    start += "<font color='white'>"
                    end += "</font>"
            ret.append(start + foo + end)    
        return ret
        
    def add_table(self, table, formats):
        self.content += """<table border="1">"""
        for idx,row in enumerate(table):
            if idx == 0:
                self.content += "<tr><th>"
                self.content += "</th><th>".join(row)
                self.content += "</th></tr>"
            else:
                self.content += "<tr><td"
                self.content += "</td><td".join(self.format_row(row, formats))
                self.content += "</td></tr>"
                    
        self.content += "</table>"
        
    def add_string(self, foo):
        self.content += foo + "<br>"

    def add_heading(self, foo):
        self.content += "<h3>" + foo + "</h3>"
    
    def get_html(self):
        return "<html><head></head><body>" + self.content + "</body></html>"
    
def main():
    log.info("Started...")
    
    # Test
    table = [ [ "", "Mike", "Dan" ], [ 5.555555,6.66666,7.77777 ]]
    formats = [ report.CONST_FORMAT_NONE, report.CONST_FORMAT_CCY_INT_COLOR, report.CONST_FORMAT_PCT ]
    r = report()
    r.add_table(table, formats)
    print(r.get_html())
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)