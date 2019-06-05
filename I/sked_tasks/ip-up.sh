#!/bin/sh

# echo.tzo.com = 216.39.81.77
IP=`wget -q -O - "http://216.39.81.77/ip.shtml" | awk -F "[: ]" '{ print $2 }'`
 
PATH_IP_HTML="/var/ip.html"
TIME=`date`

cat <<EOF > ${PATH_IP_HTML}
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<title>IP Address</title>
</head>
<body>
Time of Last IP Upload: ${TIME}<br>
IP Address: ${IP}
<br>
&bull; <a href="http://${IP}/cgi-bin/dialler.cgi?foo">Sked</a>
&bull; <a href="http://${IP}/cgi-bin/gps.cgi?foo">GPS</a>
&bull; <a href="http://${IP}:8080">Router</a>
&bull; <a href="http://${IP}:8081/netcam.jpg">NC</a>
&bull; <a href="http://${IP}:8082">PTZ</a>
</body>
</html>
EOF
