// added file pointer close on error exit ie timeouts
// this file controls the PT stage through ascii serial commands
// now using port 1 just temporarily
// begun RR 08/22/09 @ 788/rose bay


#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <time.h>		        /* ctime, asctime      */

#define BAUDRATE B9600 // for PT stage
#define SERIALPORT "/dev/ttyS1"

#define FILEOPEN1 "/var/pt_response"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

/* will be used to save old port settings */
/* will be used for new port settings */
        	
	struct termios oldtio;           	
	struct termios newtio; 
	FILE  *fp1;
	int fd ;

main(int argc, char **argv)
{

    	char string[20];
	char sentence[128];
        char buf[64] ;
	char *command , *value ;
	char str_len;
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

	if (argc == 3) 
		{
		value = argv[2];
		}
	
		// printf ("YES do %s with value = %s\n",command,value);

	  /* open files for writing */
          	
		fp1 = fopen(FILEOPEN1,"w");
          	if (fp1 < 0)
          	{
          	perror(FILEOPEN1);
		printf ("Cannot open FILEOPEN1 \n");
          	exit (-1);
          	}

          
/* ################ end of parsing args ############# */        


 		/* send cal command to do PT calibration to be output on ser 1 */
		
		strcat(command,value) ;
	        // strcat(command,"\r") ;
		 
		str_len = strlen(command) ;
		printf("Writing command = %s\n",command);

		while (write(fd,command,str_len) < str_len);
		while (write(fd,"\r",1) < 1);
		// printf("After serial port write\n");


/* ################ begin of loop for input, reading 1-n characters at a time until '\n' received  */

		timeout = 8000000;
           	do	
           	{
		res = read(fd,buf,1);   /* returns after at least 1 char has been input */
	     	timeout--;
           	}
           	while (buf[0] != '*' && buf[0] != '!' && timeout !=0);
 
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

	   timeout = 8000000;
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


/* ############### should there be a problem ############# */

	if (timeout == 0)
	time_out() ;
 
/* ############### end  ############# */


	/* restore the old port settings before quitting */

	tcsetattr(fd,TCSANOW,&oldtio);

	// printf("string_pos = %d\n",string_pos);
	// printf("%s\n",sentence);
	fprintf(fp1,"%s\n",sentence) ;
	
	close(fd);
	exit(0);

	printf("all done now\n");

// end of main
}

int time_out() 
{
		printf("timeout in PT sync\n") ;
		fprintf(fp1,"TIMEOUT in PT Sync\n") ;

 		/* restore the old port settings before quitting */
       
		tcsetattr(fd,TCSANOW,&oldtio);

		fclose(fp1);
		close(fd);
		exit(-1) ;
	
}
