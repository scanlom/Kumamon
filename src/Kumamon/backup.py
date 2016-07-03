'''
Created on Jul 22, 2013

@author: scanlom
'''

import os, zipfile, shutil, mail, config
from subprocess import call
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from log import log

def zipdir(path, zip, log):
    log.info("Zipping " + path)
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))
            log.info("Zipped " + file)

def main():
    log.info("Started...")
    
    # Clean out the temporary directory
    if os.path.exists( config.config_backup_tmp_dir ):
        shutil.rmtree( config.config_backup_tmp_dir )
    
    os.makedirs( config.config_backup_tmp_dir )
    
    # Zip up the db's (finances and wikidb)
    call("pg_dump finances | split -b 1m - " + config.config_backup_tmp_dir + "financesbackup", shell=True)
    call("pg_dump wikidb | split -b 1m - " + config.config_backup_tmp_dir + "wikidbbackup", shell=True)

    # Zip up the files we want
    for dir in config.config_backup_zip_dirs:
        zip = zipfile.ZipFile(config.config_backup_tmp_dir + dir[1], 'w')
        zipdir(dir[0], zip, log)
        zip.close()

    # Copy the backup to Dropbox
    for i in reversed( range( 0, config.config_backup_days ) ):
        dest = config.config_dropbox_dir + config.config_backup + str( i )
        if i > 0:
            src = config.config_dropbox_dir + config.config_backup + str( i - 1 )
            if os.path.exists( dest ):
                shutil.rmtree( dest )
            if os.path.exists( src ):
                os.rename( src, dest )
        else:
            shutil.move( config.config_backup_tmp_dir, dest )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  backup.py", str( err ) )