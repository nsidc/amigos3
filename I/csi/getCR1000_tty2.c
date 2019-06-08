// Modified on July 28th at Boulder
/*
$Id: getCR1000_tty2.c 16369 2010-05-03 17:08:38Z tharan $
r15742 | tharan | 2009-10-08 15:11:23 -0600 (Thu, 08 Oct 2009) | 5 lines

date: 2009/09/05 01:25:52;  author: tharan;  state: Exp;  lines: +2 -5
replaced check for end of buffer marked by carriage return with 'E'.
removed placing newline in output buffer.
removed extraneous printing of "all done now" message.

2009/12/14 Terry Haran
Changed open on SERIALPORT to O_RDONLY.
Removed writing of CR1000 string.
*/

// 2010/01/10 Terry Haran
// Changed cr1000 data file to wxt.
// Removed getting date and time.

// 2010/01/11 Terry Haran
// Removed extraneous "all done now".

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B9600 // for CR1000
#define SERIALPORT "/dev/ttyS2"

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

          /* now open the serial port for reading */        
          fd = open(SERIALPORT, O_RDONLY | O_NDELAY ); 

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
          
// ################ begin of loop for input, reading 1-n characters at a time until 'E' received        

sentence[string_pos++] = '\n'; 

timeout = 4000000;
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

	   timeout = 4000000;
           do	
           {
		res = read(fd,buf,1);   /* returns after at least 1 char has been input */
	     	timeout-- ;
			if(res)
			{
			sentence[string_pos++] = buf[0] ;
			}
           }
		while (buf[0] != 'E' && timeout !=0 ); 
	
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

// end of main
}
