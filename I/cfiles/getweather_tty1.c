// June 26th 2007 at Mona Vale
// added sscanf stuff 9/16/07
// modified for serial port 1 at Pittwater 21st March 2008


#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <string.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B19200 // for weather station Vaisala WXT510
#define SERIALPORT "/dev/ttyS1"

#define FILEOPEN1 "weather"
#define FILEOPEN2 "weatherdata"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

	struct tm *l_time;
    	char string[80];
	
	FILE  *fp1, *fp2;

	char sentence[80];
	char buf[80] ;
	char t ;
	int string_pos;
      	unsigned long timeout ;
      	int fd, res;

	char str[ ] = "This is a simple string";

	int dir,n;
	float speed,temp,humidity,pressure,volts;
	n=0;
main()
{   

          struct termios oldtio; /* will be used to save old port settings */
          struct termios newtio; /* will be used for new port settings */

	        
          /* open files for writing */
          fp1 = fopen("/var/weather","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
//		system("/mnt/gpio/radar_OFF");
          exit (-1);
          }

          fp2 = fopen("/var/weatherdata","a");
          if (fp2 < 0)
          {
//		system("/mnt/gpio/radar_OFF");
          perror(FILEOPEN2);
          exit (-1);
          }

          /* now open the serial port for reading and writing */        
          fd = open(SERIALPORT, O_RDWR | O_NDELAY ); 

          if (fd < 0) 
          {
            perror(SERIALPORT); 
//	    system("/mnt/gpio/radar_OFF");	
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
          
// ################ get the date and time        

// printf("make sure radar off \n");
// system("/mnt/gpio/radar_OFF") ;
// printf("turning radar ON \n");
// system("/mnt/gpio/radar_ON");

time_t now;		// define 'now' time_t is probably 
time(&now);

l_time = localtime(&now);
// strftime(string, sizeof string,"%m/%d/%y %H:%M:%S\n", l_time);
    strftime(string, sizeof string,"%m%d%y %H%M%S", l_time);

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
			
	// printf("out of sync grab for LF \n"); 

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

	// printf("out of CR sync \n"); 

// ####################################### end of looking for CR sync portion

}
while (parse_sentence_0R0(sentence) != 0);  

// ####################################### if we have a timeout

	if (timeout == 0)
	print_timeout();

// ####################################### store data in 2 files

// 	fprintf(fp1,"%s,%s\n",string,sentence) ;
//	fprintf(fp2,"%s,%s\n",string,sentence) ;
//	printf("%s,%s\n",string,sentence);

// new stuff
// typical string from WXT510 "0R0,Dm=337D,Sm=9.8M,Ta=16.7C,Ua=63.7P,Pa=1003.5H,Vs=12.3V"

n=sscanf(sentence,"0R0,Dm=%dD,Sm=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Vs=%fV",&dir, &speed, &temp,&humidity,&pressure,&volts) ;
printf(" Original sentence = %s \n",sentence) ;  
printf(" Return value from sscanf = %d \n",n) ;

printf("direction = %d, speed = %2.1f, temperature = %3.1f\n",dir,speed,temp) ;
printf("humidity = %3.1f, pressure = %4.1f, volts = %2.1f\n",humidity,pressure,volts) ;

fprintf(fp1,"%s %d %2.1f %3.1f %3.1f %4.1f %2.1f\n",string,dir,speed,temp,humidity,pressure,volts) ;  
fprintf(fp2,"%s %d %2.1f %3.1f %3.1f %4.1f %2.1f\n",string,dir,speed,temp,humidity,pressure,volts) ;  
printf("New sentence is %s %d %2.1f %3.1f %3.1f %4.1f %2.1f\n",string,dir,speed,temp,humidity,pressure,volts) ;  
// #######################################             	   

	/* restore the old port settings before quitting */
	tcsetattr(fd,TCSANOW,&oldtio);

	/* close files */	
	fclose(fp1);
	fclose(fp2);
	close(fd);

	 printf("all done now\n");
//	 system("/mnt/gpio/radar_OFF");

// end of main
}

int print_timeout()
{
		printf("timeout in TRACE sync @ %s\n",string) ;
		fprintf(fp1,"TIMEOUT in TRACE Sync @ %s\n",string) ;
		fprintf(fp2,"TIMEOUT in TRACE Sync @ %s\n",string) ;                                                          
//		system("/mnt/gpio/radar_OFF") ;
		fclose(fp1);
		fclose(fp2);
		close(fd);
		exit(-1) ;	
}

int parse_sentence_0R0(char *sentence) 
{ 	
if (sscanf(sentence,"0R0,Dm=%dD,Sm=%fM,Ta=%fC,Ua=%fP,Pa=%fH,Vs=%fV",&dir, &speed, &temp,&humidity,&pressure,&volts) == 6) 
	return 0; 
	else
	return -1;	 }
