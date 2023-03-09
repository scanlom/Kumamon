'''
Created on Jul 22, 2013
@author: scanlom
'''

from os import makedirs
from os import path
from os import rename
from shutil import copytree
from shutil import move
from shutil import rmtree
from subprocess import call
from lib_config import config_backup
from lib_config import config_backup_days
from lib_config import config_backup_tmp_dir
from lib_config import config_backup_zip_dirs
from lib_config import config_dropbox_dir
from lib_log import log

def main():
    log.info("Started...")
    
    # Clean out the temporary directory
    if path.exists( config_backup_tmp_dir ):
        rmtree( config_backup_tmp_dir )
    
    makedirs( config_backup_tmp_dir )
    
    # Copy the db's (finances, fujippi, and wikidb)
    call("pg_dump finances | split -b 1m - " + config_backup_tmp_dir + "financesbackup", shell=True)
    call("pg_dump fujippi | split -b 1m - " + config_backup_tmp_dir + "fujippibackup", shell=True)
    call("pg_dump wikidb -U wikiuser | split -b 1m - " + config_backup_tmp_dir + "wikidbbackup", shell=True)

    # Copy the directories we want
    for dir in config_backup_zip_dirs:
        copytree(dir[0], config_backup_tmp_dir + dir[1])

    # Copy the backup to Dropbox
    for i in reversed( range( 0, config_backup_days ) ):
        dest = config_dropbox_dir + config_backup + str( i )
        if i > 0:
            src = config_dropbox_dir + config_backup + str( i - 1 )
            if path.exists( dest ):
                rmtree( dest )
            if path.exists( src ):
                rename( src, dest )
        else:
            move( config_backup_tmp_dir, dest )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")