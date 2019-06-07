// June 26th 2007 at Mona Vale
// added sscanf stuff 9/16/07
// modified for serial port 2 at Pittwater 21st March 2008
// modified to include maximum windpseed, direction maximum, heater temperature and heater voltage
// done at Rose Bay Oct 5th 2008
//
// 2010/01/10 Terry Haran
// Changed weather file to wxt.
// Removed getting date and time.
// Removed appending to weatherdata file.
//
// 2010/01/27 Terry Haran
// Added ability to decode messages from the WXT containing "#" characters that appear when the
// unit is iced up and outputting zeros.
 
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <string.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B19200 // for weather station Vaisala WXT510
#define FILEOPEN1 "/var/wxt"
#define SERIALPORT "/dev/ttyS2"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

	struct tm *l_time;
    	char string[100];
	FILE  *fp1;

	char sentence[100];
	char buf[100] ;
	char t ;
	int string_pos;
      	unsigned long timeout ;
      	int fd, res;

	char str[ ] = "This is a simple string";

	int dir,dir_max,n;
	float speed,speed_max,temp,humidity,pressure,volts_heater,temp_heater,volts;
// 	n=0; was here till compiler complained,now in main 

main()
{   

n=0;

          struct termios oldtio; /* will be used to save old port settings */
          struct termios newtio; /* will be used for new port settings */

	        
          /* open files for writing */
          fp1 = fopen(FILEOPEN1,"w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
          exit (-1);
          }

          /* now open the serial port for reading and writing */        
          fd = open(SERIALPORT, O_RDWR | O_NDELAY ); 

          if (fd < 0) 
          {
            perror(SERIALPORT); 
            exit(-1); 
          }
          
          /* save current port settings */
          tcgetattr(fd,&oldtio); 
          
          /* initialize the port settings structure to all zeros */
          bzero(&newtio, sizeof(newtio));

          /* then set the baud rate, handshaking and a few other settings */
          newtio.c_cflag = (CBAUD & BAUDRATE);
	  newtio.c_cflag |= (CSIZE & CS8);
          newtio.c_cflag |= CREAD;

	  newtio.c_lflag &= 0x0 ;
          newtio.c_iflag = newtio.c_oflag = newtio.c_lflag ;
	  newtio.c_oflag = ONLRET;

          /* set input mode */
          newtio.c_lflag &= 0x0 ;

          // newtio.c_cc[VTIME]    = 0;   /* inter-character timer used */
          // newtio.c_cc[VMIN]     = 0;   /* will return after first char or timeout */

          tcflush(fd, TCIFLUSH);
          tcsetattr(fd,TCSANOW,&newtio);
          
// ################ begin of loop for input, reading 1-n characters at a time until '0R0; is received
// ################ first look for a LF to synchronize then read characters until a CR is received
 
timeout = 8000000;

do
{
            string_pos = 0;
            do	
            {
	res = read(fd,buf,1);   /* returns after at least 1 char has been input */
             	timeout--;
            }
            while (buf[0] !='\n' && string_pos == 0 && timeout !=0);  

	if (timeout == 0)
	print_timeout();
			
	printf("out of sync grab for LF \n"); 

// ####################################### end of looking for LF sync portion

            do	
            {
	res = read(fd,buf,1);   /* returns after at least 1 char has been input */
		if(res)
                	{
                	sentence[string_pos++] = buf[0] ;
                	}
             	timeout--;
            }
            while (buf[0] !='\r' && timeout !=0);  
            sentence[string_pos] = 0; 

	if (timeout == 0)
	print_timeout();

	printf("out of CR sync \n"); 

// ####################################### end of looking for CR sync portion

}
while (parse_sentence_0R0_all(sentence) != 0);  

// ####################################### if we have a timeout

	if (timeout == 0)
	print_timeout();

// ####################################### store data in 1 file

// 	fprintf(fp1,"%s,%s\n",string,sentence) ;
//	printf("%s,%s\n",string,sentence);

// new stuff
// typical string from WXT510 // "0R0,Dm=103D,Dx=134D,Sm=0.1M,Sx=0.1M,Ta=24.7C,Ua=48.3P,Pa=1013.1H,Th=24.5C,Vh=0.0N,Vs=7.4V"

n=sscanf(sentence,"0R0,Dm=%dD,Dx=%dD,Sm=%fM,Sx=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fN,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) ;
printf(" Original sentence = %s \n",sentence) ;  
// printf(" Return value from sscanf = %d \n",n) ;

printf("direction = %d,dir_max = %d,speed = %2.1f,speed_max = %2.1f,temperature = %3.1f\n",dir,dir_max,speed,speed_max, temp) ;
printf("humidity = %3.1f,pressure = %4.1f,volts_heater = %2.1f,temp_heater = %2.1f,volts = %2.1f\n",humidity,pressure,volts_heater,temp_heater,volts) ;

fprintf(fp1,"%s %d %2.1f %3.1f %3.1f %4.1f %2.1f %d %2.1f %2.1f %2.1f\n", string,dir,speed,temp,humidity,pressure,volts,dir_max,speed_max,volts_heater,temp_heater); 

printf("New sentence is %s %d %2.1f %3.1f %3.1f %4.1f %2.1f %d %2.1f %2.1f %2.1f\n", string,dir,speed,temp,humidity,pressure,volts,dir_max,speed_max,volts_heater,temp_heater) ;
 
// #######################################             	   

	/* restore the old port settings before quitting */
	tcsetattr(fd,TCSANOW,&oldtio);

	/* close files */	
	fclose(fp1);
	close(fd);

	printf("all done now\n");

// end of main
}

int print_timeout()
{
		printf("timeout in TRACE sync @ %s\n",string) ;
		fprintf(fp1,"TIMEOUT in TRACE Sync @ %s\n",string) ;
		fclose(fp1);
		close(fd);
		exit(-1) ;	
}

int parse_sentence_0R0_all(char *sentence) 
{ 	
if 
( 
(sscanf(sentence,"0R0,Dm=%dD,Dx=%dD,Sm=%fM,Sx=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fN,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10) 
|| 
(sscanf(sentence,"0R0,Dm=%dD,Dx=%dD,Sm=%fM,Sx=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fV,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
||
(sscanf(sentence,"0R0,Dm=%dD,Dx=%dD,Sm=%fM,Sx=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fW,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
||
(sscanf(sentence,"0R0,Dm=%dD,Dx=%dD,Sm=%fM,Sx=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fF,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
||
(sscanf(sentence,"0R0,Dm=%d#,Dx=%d#,Sm=%f#,Sx=%f#,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fN,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10) 
|| 
(sscanf(sentence,"0R0,Dm=%d#,Dx=%d#,Sm=%f#,Sx=%f#,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fV,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
||
(sscanf(sentence,"0R0,Dm=%d#,Dx=%d#,Sm=%f#,Sx=%f#,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fW,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
||
(sscanf(sentence,"0R0,Dm=%d#,Dx=%d#,Sm=%f#,Sx=%f#,Ta=%fC,Ua=%fP,Pa=%fH,Th=%fC,Vh=%fF,Vs=%fV",
&dir,&dir_max,&speed,&speed_max,&temp,&humidity,&pressure,&temp_heater,&volts_heater,&volts) == 10)
)
	return 0; 
	else
	return -1 ;	 }

