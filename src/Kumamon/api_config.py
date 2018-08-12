'''
Created on Dec 26, 2013

@author: scanlom
'''

from configparser import SafeConfigParser
from os import path

config = SafeConfigParser()
config.read(path.expanduser('~/.Kumamon'))
config_email_server         = config.get('Email','Server')
config_email_port           = config.getint('Email','Port')
config_email_user           = config.get('Email','User')
config_email_password       = config.get('Email','Password')
config_email_fumi           = config.get('Email','Fumi')
config_database_connect     = config.get('Database','Connect')
config_database2_connect    = config.get('Database2','Connect')

config_backup           = 'Backup'
config_dropbox_dir      = path.expanduser('~/Dropbox/') + config_backup + '/'
config_backup_days      = 5
config_backup_tmp_dir   = path.expanduser('~/') + config_backup + '/'
config_backup_zip_dirs  = [ 
                [ path.expanduser('~/Mike'), 'Mike' ], 
                [ path.expanduser('~/bin'), 'bin' ],
                [ path.expanduser('~/misc'), 'misc' ],
                [ path.expanduser('~/dev'), 'dev' ],                
                [ path.expanduser('~/.vim'), '.vim' ],                
            ] 

