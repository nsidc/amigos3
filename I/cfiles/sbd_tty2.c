// Modified at Rose Bay Sept 11 2008

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B9600 // for CR1000
#define SERIALPORT "/dev/ttyS2"

#define FILEOPEN1 "CR1000"
#define FILEOPEN2 "CR1000data"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

main()
{

	struct tm *l_time;
    	char string[20];
	
	FILE  *fp1, *fp2;

	char sentence[2048];
        char buf[64] ;
	int string_pos;
        string_pos = 0;
	unsigned long timeout ;
        int fd, res;
      

          struct termios oldtio; /* will be used to save old port settings */
          struct termios newtio; /* will be used for new port settings */

	  /* first open the serial port for reading and writing */
        
          fd = open(SERIALPORT, O_RDWR | O_NDELAY ); 

          if (fd < 0) 
          {
            perror(SERIALPORT); 
	   //  system("/mnt/gpio/radar_OFF");	
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
          
// ################ begin of loop for input, reading 1-n characters at a time until 'T' received        

time_t now;		// define 'now' time_t is probably 
time(&now);

l_time = localtime(&now);
strftime(string, sizeof string,"%m/%d/%y %H:%M:%S\n", l_time);

sentence[string_pos++] = '\n'; 

printf("sending reset to modem\n") ;

while (write(fd,"ATZ\r",4) < 4) ;
tickDelay(3000);
printf("sending msg to modem\n") ;
while (write(fd,"AT+SBDWT=hello Wx8\r",19) < 19) ;
tickDelay(3000);
printf("sending send cmd to modem\n") ;
while (write(fd,"AT+SBDI\r",8) < 8) ;
tickDelay(3000);
printf("all done\n") ;

	/* restore the old port settings before quitting */

	tcsetattr(fd,TCSANOW,&oldtio);

	// printf("string_pos = %d\n",string_pos);
	printf("%s\n",sentence);
		
	close(fd);
	exit(0);

	printf("all done now\n");
}

// end of main

/* ********************************************************************** */

int tickDelay(int dly)
{

// printf("in delay\n");

int t;
while (dly !=0)
	{
	for (t=0;t<90000;t++); // was org 7
	dly--;
	}
}
/* ********************************************************************** */

