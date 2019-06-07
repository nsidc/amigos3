#! /bin/bash

### CHECK #########

HOST='192.168.0.66'
USER='dts'

###########################################
#     ftp check if .ddf files exist        #
###########################################
checkfile(){
echo "inside checkfile & i="$i  
sleep 1
ftp -n $HOST <<EOF 
quote USER $USER
quote PASS $PASSWD
ls "channel\ ${i}.ddf"
quit
EOF
}


for i in {1..4}
do
  checkfile
  echo "i = "$i
  sleep 1
#  if checkfile then
#    echo ".DDF file exists..."
     
#     ftp -n $HOST <<END_SCRIPT
#     quote USER $USER
#     quote PASS $PASSWD
#     ascii
#     prompt off
#     lcd /var/tmp/

#     get channel\ 1.ddf channel1.ddf
#     get channel\ 1.dtd channel1.dtd
#     get channel\ 1.tdf channel1.tdf
#     get channel\ 3.ddf channel2.ddf
#     get channel\ 3.dtd channel2.dtd
#     get channel\ 3.tdf channel2.tdf

#     mdelete *.*
#     quit
#     END_SCRIPT
#     FTP_RETURN=$?
#        echo "----- FTP_RETURN: $FTP_RETURN"
     #   echo "----- FTP_RETURN: $FTP_RETURN" > $PORT
#  else
#     echo "ddf not found: "$NOW >> 
/var/tmp/workspace/DTSdata_err_log_Trit$
#  fi
done

exit 0
