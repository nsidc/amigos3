#Copies data from windows to Linux over ssh server using Linux
import paramiko

#Defines variables for login
hostname = '192.168.0.50'
username = 'admin'
password = 'admin'

#Defines paths to data files
windows_filepath = '/Desktop/DTS_data/XT17057/temperature/'
linux_filepath = '/media/mmcblk0p1/dts'

#ssh login to windows from linux
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname, username, password)

#ftp command to get dts data
ftp_client = ssh_client.open_sftp()
ftp_client.get(windows_filepath,linux_filepath)
ftp_client.close()



from pyssh.session import Session
session = Session()
ftp = session.createftp()
ftp.get("Desktop/","/media/mmcblk0p1/dts/")