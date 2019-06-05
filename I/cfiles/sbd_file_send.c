// August  9th 2007 at Mona Vale

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>

#define BAUDRATE B9600 // for SBD
#define SERIALPORT "/dev/ttyS1"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

	FILE *fp1;
	unsigned char ch1, low_byte, high_byte ; 	 
	unsigned int char_sum, two_byte_file_sum ; 	  
	int fd, n, length;
	unsigned long j;
	unsigned char bin_data[2048];
      char thousands, hundreds, tens, units, buf[8] ;
	struct termios oldtio; /* will be used to save old port settings */
      struct termios newtio; /* will be used for new port settings */

int main(int argc, char *argv[]) 
{
	
  if(argc!=2) {
    printf("Usage: must specify file.gz \n");
    exit(1);
  }

	char_sum = 0;
      two_byte_file_sum = 0; 	

  /* open first file */
  if((fp1 = fopen(argv[1], "rb"))==NULL) {
    printf("Cannot open first file.\n");
    exit(1);
  }

// call function for opening serial port   
  open_serial_port();

// call function for reading bytes into array, calculating checksum and file length
read_file_into_array();


// ------------------- reset the port

n = write(fd,"ATZ\n\r",5);
if(n < 0)
printf("serial port write failed\n");

printf("Waiting\n");
for(j=0;j<0x4ffffff;j++);

// figure how many bytes to send and separate that into 
thousands = length / 1000 ; 
hundreds = (length % 1000) / 100 ; 
tens = ((length % 1000) % 100) / 10 ;
units = (((length % 1000) % 100) % 10 ) ;

// printf ("how many thousands are there %d\n",thousands);
// printf ("how many hundreds are there %d\n",hundreds);
// printf ("how many tens are there %d\n",tens);
// printf ("how many units are there %d\n",units);

n = write(fd,"at+sbdwb=",9);
if(n < 0)
printf("serial port write failed\n");

printf("Waiting\n");
for(j=0;j<0xffffff;j++);

// length of file in chars and convert to ascii for sbdwb command

buf[0] = (0x30 + thousands) ;
buf[1] = (0x30 + hundreds) ;
buf[2] = (0x30 + tens) ;
buf[3] = (0x30 + units) ;

n = write(fd,buf,4);
if(n < 0)
printf("serial port write failed\n");

// end of the command setup
n = write(fd,"\r\n",2);
if(n < 0)
printf("serial port write failed\n");

printf("Waiting\n");
for(j=0;j<0x4ffffff;j++);

printf("Sending file data \n");

n = write(fd,bin_data,length);   /* 1 char at a time output only */
if(n < 0)
printf("serial port write failed\n");

// now send two byte checksum, high byte then low byte
buf[0] = high_byte ;
n = write(fd,buf,1);
if(n < 0)
printf("serial port write failed\n");

buf[0] = low_byte ;
n = write(fd,buf,1);
if(n < 0)
printf("serial port write failed\n");

printf("Waiting\n");
for(j=0;j<0x4ffffff;j++);

n = write(fd,"at+sbdi\r\n",9);
if(n < 0)
printf("serial port write failed\n");

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
  /* rad contents of the file and store in the array */
  
    while(!feof(fp1)) {
    ch1 = fgetc(fp1);
    	if(ferror(fp1)) {
      	printf("Error reading from file.\n");
		/* restore the old port settings before quitting */
		tcsetattr(fd,TCSANOW,&oldtio);
      	exit(1);
    			}

    bin_data[length] = ch1 ; 	
    char_sum += (unsigned int)ch1 ;
    length++;
    // printf("Sum number = %4d, Current char = %2x, Sum of file so far = %5x\n",length,ch1, char_sum);
  }
	length = length -1 ; // reduce the total chars due to length++
      char_sum = char_sum - 0xff ; // need to remove the EOF
      two_byte_file_sum = char_sum & 0xffff ;
      low_byte = (unsigned char) (two_byte_file_sum & 0xff) ;
      high_byte = (unsigned char) ( (two_byte_file_sum & 0xff00) >> 8) ;
      
      printf("Total chars = %4d, Sum of all chars in file = %5x.\n",length,char_sum);
      printf("Two byte file sum = %4x, high_byte = %4x, low_byte = %4x.\n",two_byte_file_sum,high_byte,low_byte);

if(length > 1959) 
		{
      	printf("File too big for SBD binary mode\n");
		/* restore the old port settings before quitting */
		tcsetattr(fd,TCSANOW,&oldtio);
		fclose(fp1);
      	exit(1);				
		}
		return ;
}
