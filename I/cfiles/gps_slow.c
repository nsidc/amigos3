	
	#include <sys/types.h>
        #include <sys/stat.h>
        #include <fcntl.h>
        #include <termios.h>
        #include <stdio.h>

        // #define BAUDRATE B38400
        #define BAUDRATE B4800 // for GARMIN GPS 
        #define SERIALPORT "/dev/ttyS0"
         
        #define CINBUFSIZE 127
        #define COUTBUFSIZE 127

	#define MAX_SENTENCE 100 

// names of days of week
const char dayname[7][4] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
const char monthname[12][4] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
	"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};

// GPSPosition current_pos;
// struct tm current_time;

        main()

        {

	char sentence[MAX_SENTENCE];
	int input_char;
	int string_pos;
	char dir_string[2];
	string_pos = 0;
	dir_string[1] = 0;

          int fd,c, res;

          struct termios oldtio; /* will be used to save old port settings */

          struct termios newtio; /* will be used for new port settings */

          char buf[255];         /* buffer used to store received characters */

          
          /* first open the serial port for reading and writing */

          fd = open(SERIALPORT, O_RDWR | O_NOCTTY ); 

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

          newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
          newtio.c_iflag = IGNPAR;
          newtio.c_oflag = 0;
          

          /* set input mode (non-canonical, no echo,...) */

          newtio.c_lflag = 0;

          newtio.c_cc[VTIME]    = 1;   /* inter-character timer unused */

          newtio.c_cc[VMIN]     = 1;   /* blocking read until first char received */
          

          tcflush(fd, TCIFLUSH);

          tcsetattr(fd,TCSANOW,&newtio);

  

          /* loop for input, reading 1-255 characters at a time until 'z' received */        

          while (1) 

          {

            res = read(fd,buf,255);   /* returns after at least 1 char has been input */

           buf[res]=0;               /* zero-terminate the string */  

           printf(":%s:%d\n", buf, res);
/*
		// input_char = serCgetc();
		if(buf[0] == '\r' || buf[0] == '\n')

		{
			sentence[string_pos] = 0; //add null
			printf("%s\n", sentence);
			string_pos = 0;
		}
		else 
		if(buf[0] > 0)
		{
			sentence[string_pos] = buf[0];
			string_pos++;
			// if(string_pos == MAX_SENTENCE)
			//	string_pos = 0;	//reset string if too large
		}
*/  
        }
  
          /* restore the old port settings before quitting */

          tcsetattr(fd,TCSANOW,&oldtio);

        
}
