'''
Created on Sep 1, 2025
@author: scanlom
'''

import api_blue_lion as _abl

portfolios = _abl.portfolios()
recon = 0
for p in portfolios:
    print( p['name'])
    recon += p['cash'] - p['debt']
print( recon )