'''
Created on Aug 13, 2018

@author: scanlom
'''

from api_log import log

class report:
    CONST_FORMAT_NONE   = 0
    CONST_FORMAT_CCY    = 1
    CONST_FORMAT_PCT    = 2    
    
    def __init__(self):
        self.content = ""
    
    def format_ccy(self, number):
        return '{0:,.2f}'.format(number)

    def format_pct(self, number):
        return '%{0:,.2f}'.format(100*number)
    
    def format_row(self, row, formats):
        ret = []
        for item,format in zip(row, formats):
            if self.CONST_FORMAT_NONE == format:
                ret.append(str(item))
            elif self.CONST_FORMAT_CCY == format:
                ret.append(self.format_ccy(item))
            elif self.CONST_FORMAT_PCT == format:
                ret.append(self.format_pct(item))
                
        return ret
        
    def add_table(self, table, formats):
        self.content += """<table border="1">"""
        for idx,row in enumerate(table):
            if idx == 0:
                self.content += "<tr><th>"
                self.content += "</th><th>".join(row)
                self.content += "</th></tr>"
            else:
                self.content += "<tr><td>"
                self.content += "</td><td>".join(self.format_row(row, formats))
                self.content += "</td></tr>"
                    
        self.content += "</table>"
        
    def add_string(self, str):
        self.content += str + "<br>"
    
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