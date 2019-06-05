// August  9th 2007 at Mona Vale
// reworked at 8/788 NSH Rose Bay 9/15/08

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>

#define BAUDRATE B9600 // for SBD
#define SERIALPORT "/dev/ttyS2"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

	FILE *fp1;
	unsigned char ch1; 	 
	int fd, n, length;
	unsigned long j;
	unsigned char ascii_data[128];
	struct termios oldtio; /* will be used to save old port settings */
        struct termios newtio; /* will be used for new port settings */

int main(int argc, char *argv[]) 
{
	
  if(argc!=2) {
    printf("Usage: must specify file\n");
    exit(1);
  }
	

  /* open first file */
  if((fp1 = fopen(argv[1], "r"))==NULL) {
    printf("Cannot open file\n");
    exit(1);
  }

// call function for opening serial port   
	open_serial_port();

// call function for reading bytes into array, calculating checksum and file length
	read_file_into_array();


// ------------------- reset the port

n = write(fd,"ATZ\n\r",5);
if(n < 0)
printf("Serial port Write ATZ failed\n");

printf("Waiting\n");
for(j=0;j<0x4ffffff;j++);

n = write(fd,"at+sbdwt=",9);
if(n < 0)
printf("serial port write at+sbdwt failed\n");

printf("Waiting after sbdwt\n");
for(j=0;j<0xffffff;j++);

n = write(fd,ascii_data,length);
if(n < 0)
printf("serial port write ascii data failed\n");

// end of the command setup
n = write(fd,"\r\n",2);
if(n < 0)
printf("serial port write command failed\n");

printf("Waiting after write data to modem command\n");
for(j=0;j<0x4ffffff;j++);
for(j=0;j<0x4ffffff;j++);

n = write(fd,"at+sbdi\r\n",9);
if(n < 0)
printf("serial port write send command failed\n");

printf("Waiting after sbdi command\n");
for(j=0;j<0x8ffffff;j++);
for(j=0;j<0x4ffffff;j++);

	/* restore the old port settings before quitting */
	tcsetattr(fd,TCSANOW,&oldtio);	
	fclose(fp1);

	// NOT sure why I need to comment out the next line.
	// close(fd);
	
	printf("all done now\n");
	
} // end of main

open_serial_port()
{
          	        
          /* first open the serial port for reading and writing */
        
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
	    return ;
 }

read_file_into_array()
{
   length = 0;
  /* read contents of the file and store in the array */
  
    while(!feof(fp1)) {
    ch1 = fgetc(fp1);
    	if(ferror(fp1)) {
      	printf("Error reading from file.\n");
		/* restore the old port settings before quitting */
		tcsetattr(fd,TCSANOW,&oldtio);
      	exit(1);
    			}

	ascii_data[length] = ch1 ; 	
	length++;
 			}
	length = length -1 ; // reduce the total chars due to length++
	printf("total chars = %d \n",length);

	// printf("ascii_data = %s\n",ascii_data);

if(length > 116) 
		{
      	printf("File exceeds 116 bytes...too big\n");
		/* restore the old port settings before quitting */
		tcsetattr(fd,TCSANOW,&oldtio);
		fclose(fp1);
      	exit(1);				
		}
		return ;
}
