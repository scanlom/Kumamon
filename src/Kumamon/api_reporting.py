'''
Created on Aug 13, 2018

@author: scanlom
'''

from api_log import log

class report:
    CONST_FORMAT_NONE       = 0
    CONST_FORMAT_CCY        = 1
    CONST_FORMAT_CCY_COLOR  = 2
    CONST_FORMAT_PCT        = 3 
    
    def __init__(self):
        self.content = ""
    
    def format_ccy(self, number):
        return '{0:,.2f}'.format(number)

    def format_pct(self, number):
        return '%{0:,.2f}'.format(100*number)
    
    def format_row(self, row, formats):
        ret = []
        for item,f in zip(row, formats):
            start = ""
            end = ""
            foo = ""
            if self.CONST_FORMAT_CCY == f or self.CONST_FORMAT_CCY_COLOR == f or self.CONST_FORMAT_PCT == f:
                start = " style='text-align:right'"
            start += ">"
            if self.CONST_FORMAT_CCY_COLOR == f:
                if item > 0:
                    start += "<font color='green'>"
                else:
                    start += "<font color='red'>"
                end += "</font>"
            if self.CONST_FORMAT_NONE == f:
                foo += str(item)
            elif self.CONST_FORMAT_CCY == f or self.CONST_FORMAT_CCY_COLOR == f:
                foo += self.format_ccy(item)
            elif self.CONST_FORMAT_PCT == f:
                foo += self.format_pct(item)
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
    
    def get_html(self):
        return "<html><head></head><body>" + self.content + "</body></html>"
    
def main():
    log.info("Started...")
    
    # Test
    table = [ [ "", "Mike", "Dan" ], [ 5.555555,6.66666,7.77777 ]]
    formats = [ report.CONST_FORMAT_NONE, report.CONST_FORMAT_CCY, report.CONST_FORMAT_PCT ]
    r = report()
    r.add_table(table, formats)
    print(r.get_html())
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)