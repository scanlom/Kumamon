'''
Created on Dec 26, 2013
@author: scanlom
'''

from configparser import SafeConfigParser
from os import path

config = SafeConfigParser()
config.optionxform=str  # Read Case Sensitive
config.read(path.expanduser('~/.Kumamon'))
config_email_server         = config.get('Email','Server')
config_email_port           = config.getint('Email','Port')
config_email_user           = config.get('Email','User')
config_email_password       = config.get('Email','Password')
config_database_connect     = config.get('Database','Connect')
config_database2_connect    = config.get('Database2','Connect')
config_ofx_symbols          = config._sections['OfxSymbols']
config_ofx_user1            = config.get('Ofx', 'User1')
config_ofx_pass1            = config.get('Ofx', 'Pass1')
config_ofx_acct1            = config.get('Ofx', 'Acct1')
config_ofx_user2            = config.get('Ofx', 'User2')
config_ofx_pass2            = config.get('Ofx', 'Pass2')
config_ofx_acct2            = config.get('Ofx', 'Acct2')

config_backup           = 'Backup'
config_dropbox_dir      = path.expanduser('~/Dropbox/') + config_backup + '/'
config_backup_days      = 5
config_backup_tmp_dir   = '/mnt/data/' + config_backup + '/'
config_backup_zip_dirs  = [ 
                [ path.expanduser('~/Mike'), 'Mike' ], 
                [ path.expanduser('~/bin'), 'bin' ],
                [ path.expanduser('~/misc'), 'misc' ],
                [ path.expanduser('~/dev'), 'dev' ],                
                #[ path.expanduser('~/.vim'), '.vim' ], # 2023/02/15 - Stopped using Vim with Mint Vera (tear)
            ] 

