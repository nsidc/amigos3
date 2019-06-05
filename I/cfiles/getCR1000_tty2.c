// Modified on July 28th at Boulder

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


while (write(fd,"CR1000\r",7) < 7) ;


timeout = 2000000;
           	do	
           	{
		res = read(fd,buf,1);   /* returns after at least 1 char has been input */
	     	timeout--;
           	}
           	while (buf[0] != 'B' && timeout !=0);
 
		// stuff first char in sentence
		sentence[string_pos++] = buf[0] ;

	if (timeout == 0)
		{
		printf("timeout in TRACE sync @ %s\n",string) ;
		close(fd);
		exit(-1) ;
		}
		
		// printf("out of sync grab = %c \n", buf[0]); 

// ####################################### end of sync portion

	   timeout = 2000000;
           do	
           {
		res = read(fd,buf,1);   /* returns after at least 1 char has been input */
	     	timeout-- ;
			if(res)
			{
			sentence[string_pos++] = buf[0] ;
			}
           }
		while (buf[0] != '\r' && timeout !=0 ); 
	
		sentence[string_pos++] = '\n'; 
		sentence[string_pos++] = 0; 

		if (timeout == 0)
		{
		printf("timeout in CR1000 data\n") ;
		close(fd);
		exit(-1) ;
		}

	/* restore the old port settings before quitting */

	tcsetattr(fd,TCSANOW,&oldtio);

	// printf("string_pos = %d\n",string_pos);
	printf("%s\n",sentence);
		
	close(fd);
	exit(0);

	printf("all done now\n");

// end of main
}
