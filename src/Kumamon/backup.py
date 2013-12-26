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
    
    if os.path.exists( config.config_backup_tmp_dir ):
        shutil.rmtree( config.config_backup_tmp_dir )
    
    os.makedirs( config.config_backup_tmp_dir )
    
    call("pg_dump finances | split -b 1m - " + config.config_backup_tmp_dir + "dbbackup", shell=True)

    for dir in config.config_backup_zip_dirs:
        zip = zipfile.ZipFile(config.config_backup_tmp_dir + dir[1], 'w')
        zipdir(dir[0], zip, log)
        zip.close()

    msg = MIMEMultipart()
    
    files = os.listdir(config.config_backup_tmp_dir)
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(config.config_backup_tmp_dir + f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    mail.send_mail_msg('User', 'Backup', msg)
    
    shutil.rmtree(config.config_backup_tmp_dir)
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  backup.py", str( err ) )