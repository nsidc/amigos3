// added file pointer close on error exit ie timeouts
// this file controls the PT stage through ascii serial commands
// now using port 1 just temporarily
// begun RR 08/22/09 @ 788/rose bay
// test to find out response time of Wx7 and Wx8

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B9600 // for PT stage
// for triton 
#define SERIALPORT "/dev/ttyS1"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

/* will be used to save old port settings */
/* will be used for new port settings */
        	
	struct termios oldtio;           	
	struct termios newtio; 
	FILE  *fp1;
	int fd ;

      struct tm *l_time;  
    	char string[20];
      char *command , *value ;
	char str_len;


main(int argc, char **argv)
{

	char sentence[128];
      char buf[64] ;
	char t , do_cal, do_pp , do_tp , ppval, tpval ; 
	        
	int res;
	int string_pos;
        
        unsigned long timeout ;
	
        string_pos = ppval = tpval = 0;
	t = do_cal = do_pp = do_tp = 0;
	
/* ################# serial port setup #############  */


	/* *************** first open the serial port for reading and writing */
        
          fd = open(SERIALPORT, O_RDWR | O_NDELAY ); 

          if (fd < 0) 
          {
            perror(SERIALPORT);
            printf("Cannot open serial port\n") ; 
            exit(-1); 
          }
          
	/* **************** save current port settings */

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
	  // do another flush
	  tcflush(fd, TCIFLUSH);

/* ################# end of serial port setup #############  */


/* ################# interpret any args passed on command line ############# */
	
 	if(argc > 1)
		{
		command = argv[1];
		value = "";
		// printf("Yes do command is %s\n",command) ;
		}	
	else
		{
		printf("No args with command !!\n");
		exit(-1);
		}
 

          
/* ################ end of parsing args ############# */        


 		/* send command to be output on ser 1 */
		strcat(command,value) ;
	        // strcat(command,"\r") ;
		 
		str_len = strlen(command) ;
		printf("Writing command = %s\n",command);

		while (write(fd,command,str_len) < str_len);
		while (write(fd,"\r",1) < 1);

time_t now;		// define 'now' time_t is probably 
time(&now);

l_time = localtime(&now);
strftime(string, sizeof string,"%m/%d/%y %H:%M:%S\n", l_time);
printf("Send Dial CMD @ %s\n",string) ;

	// printf("After serial port write\n");



// ####################################### end of sync portion
while(1) 
{
	   string_pos = 0;	
	   timeout = 1000000;
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
		if (strlen(sentence) > 2)
		printf("%s\n",sentence);
		if (timeout == 0)
	      time_out() ;
}

/* ############### should there be a problem ############# */

 
/* ############### end  ############# */


	/* restore the old port settings before quitting */

	tcsetattr(fd,TCSANOW,&oldtio);

	printf("string_pos = %d\n",string_pos);
	printf("%s\n",sentence);
		
	close(fd);
	exit(0);

	printf("all done now\n");

// end of main
}

int time_out() 
{
		time_t now;		// define 'now' time_t is probably 
		time(&now);

		l_time = localtime(&now);
		strftime(string, sizeof string,"%m/%d/%y %H:%M:%S\n", l_time);

		printf("End of Dial CMD @ %s\n",string) ;
		/* send command to be output on ser 1 */

		/* restore the old port settings before quitting */
       
		tcsetattr(fd,TCSANOW,&oldtio);

		close(fd);
		exit(-1) ;
	
}
