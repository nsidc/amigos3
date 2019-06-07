// 2010/01/11 Terry Haran
// getgps_alt_tty1.c derived from getgps_grs_tty1.c
//
// 2010/01/12 Terry Haran
// Fixed indentations.
// Added disabling all messages before enabling RMC message. 
//
// 2010/01/14 Terry Haran
// Added turning on GLONASS.
//
// 2010/01/18 Terry Haran
// Set external antenna.
//
// 2010/01/19 Terry Haran
// Added disabling D1 and D2 which seems to enable S1 and S2.

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>

#define BAUDRATE B115200 // default rate for grs GPS
#define FILEOPEN1 "/var/alt"
#define SERIALPORT "/dev/ttyS1"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

char buf2[128];
unsigned long timeout ;
char mode_gps;
char mode_glonass;
FILE  *fp1;

main()
{
  char sentence[128];
  char buf[128] ;
  int string_pos;
  string_pos = 0;
  char t;
        
  int fd,c, res;
  long looper;

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


  // send this command to specify use of the external antenna
  while (write(fd,"set,/par/ant/rcv/inp,ext\r", 25) < 25);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of set external antenna\n");

  // send this command to disable all messages
  while (write(fd,"dm\r", 3) < 3);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable all\n");

  // send this command to disable sending D1 data
  while (write(fd,"dm,,/msg/jps/D1\r", 16) < 16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D1\n");

  // send this command to disable sending D2 data
  while (write(fd,"dm,,/msg/jps/D2\r", 16) < 16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D2\n");

  // send this command to enable GLONASS
  while (write(fd,"set,lock/glo/fcn,y\r", 19) < 19);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of enable GLONASS\n");

  // send this command to enable GNGNS messages
  while (write(fd,"em,,/msg/nmea/GNS\r",28) < 28);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of enable GNS\n");

  /* loop for input, reading 1-255 characters at a time until 'z' received */

  looper = 16000000; // 16000000 is ~ 10 minutes & 4440000 = about 180 seconds

  while (looper >0) 
    {
      timeout = 800000;
      do	
	{
	  res = read(fd,buf,127);   /* returns after at least 1 char has been input */
	  timeout--;
	}
      while (buf[0] !='$' && string_pos == 0 && timeout !=0);

      if (timeout == 0)
	{
	  fprintf(stderr, "timeout in $GNGNS sync\n") ;
	  fprintf(fp1, "TIMEOUT in $GNGNS Sync\n") ;
	  looper = 1;

	  /* restore the old port settings before quitting */
	  tcsetattr(fd,TCSANOW,&oldtio);

	  fclose(fp1);
	  close(fd);
	  exit(-1) ;
	}

      t= 0;
      while(t!=res)
	{
	  sentence[string_pos] = buf[t] ;
	  string_pos++;
	  t++; 
	  if (buf[t] == '\r' || buf[t] == '\n')
	    {
	      sentence[string_pos] = 0;
	      // fprintf(stderr, "%s\n",sentence);
	      // fprintf(stderr, "out of grab characters\n"); // debug only

	      // typical string
	      // $GNGNS,235159.00,6412.2488396,S,05836.1276041,W,AN,07,1.49,-8.1839,13.9125,,*45

	      if(gps_get_position(sentence) == 0)
		{
		  if (mode_gps == 'A' && mode_glonass == 'A')
		    {
		      fprintf(fp1, "%s\n",buf2);
		      // fprintf(stderr, "got good acquisition\n");
		      looper = 0; // quit program now we got one good $GNGNS
		    }
		  else
		    {
		      fprintf(stderr, "Invalid Fix\n");
		    }
		}
	      string_pos = 0;
	      t = res;
	    }
	}
      looper--;
    }
  
  /* restore the old port settings before quitting */

  tcsetattr(fd,TCSANOW,&oldtio);
  
  // fprintf(stderr, "Sentence = %s\n",sentence);
  // fprintf(stderr, "looper = %d\n",looper);

  /* close files */
  fclose(fp1);
  close(fd);

  fprintf(stderr, "all done now\n");

  // end of main
}

//can parse GNGNS sentence
int gps_get_position(char *sentence)
{
  int i;

  if(strncmp(sentence, "$GNGNS", 6) == 0)
    {
      strcpy(buf2,sentence);
      // fprintf(stderr, "Sentence = %s\n",buf2);
      //parse GNS sentence
      for(i = 0;i < 6;i++)
	{
	  sentence = strchr(sentence, ',');
	  if(sentence == NULL)
	    return -1;
	  sentence++; //first character in field
	  //pull out data
	  if(i == 5) // mode
	    {
	      sscanf(sentence, "%c%c",
		     &mode_gps, &mode_glonass);
	      // fprintf(stderr, "mode_gps:%c\n", mode_gps);
	      // fprintf(stderr, "mode_glonass:%c\n", mode_glonass);
	    }
	}
    }
  else
    {
      return -1; //unknown sentence type
    }
  return 0;	
}
