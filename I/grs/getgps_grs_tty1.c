// added file pointer close on error exit ie timeouts
// changed for port 2
// moved storage to /var from /mnt RR 11/18/08 @ rose bay
// moved back to port 1
// altered to work with TG-3 
// baud rate 115k2 and string to be parsed is now $GNRMC
// renamed grs @ RB 11/7/09
//
// Nov 22 2009 Terry Haran
// Updated to include 2009/08/21 changes in getgps_tty1.c.
//
// 2010/01/10 Terry Haran
// Removed writing buf to grs.
// Renamed grsdata file to grs.
//
// 2010/01/11 Terry Haran
// Changed grs data file to gps.
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
#define FILEOPEN1 "/var/gps"
#define SERIALPORT "/dev/ttyS1"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

int lat_degrees;
int lon_degrees;
float lat_minutes;
float lon_minutes;
char lat_direction;
char lon_direction;
char link_quality;

int year,month,day,hours,minutes,seconds;
char buf2[128];
unsigned long timeout ;
char *mydate="date ";
FILE  *fp1;

main(int argc, char **argv)
{
  char sentence[128];
  char buf[128] ;
  int string_pos;
  string_pos = 0;
  char t, update_datetime;
        
  update_datetime = 0;
        
  int fd,c, res;
  long looper;

  struct termios oldtio; /* will be used to save old port settings */
  struct termios newtio; /* will be used for new port settings */

  if ( (argc == 2) && (strcmp(argv[1],"-u")==0) )
    {
      fprintf(stderr, "YES datetime update\n");
      update_datetime = 1;
    }
  else
    {
      fprintf(stderr, "NO datetime update\n");
      update_datetime = 0;
    }
      
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
  while (write(fd,"dm,/dev/ser/a\r", 14) < 14);
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

  // send this command to enable GNRMC messages
  while (write(fd,"em,,/msg/nmea/RMC\r",28) < 28);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of enable RMC\n");

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
	  fprintf(stderr, "timeout in $GNRMC sync\n") ;
	  fprintf(fp1, "TIMEOUT in $GNRMC Sync\n") ;
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
	      // $GNRMC,103053.00,A,3351.9864389,S,15116.2812749,E,0.1244,106.230,270109,12.543,W,A*2D

	      if(gps_get_position(sentence) == 0)
		{
		  if (link_quality == 'A')
		    { 
		      // fprintf(stderr, "Time: %02d:%02d:%02d\n",hours,minutes,seconds);
		      // fprintf(stderr, "Date: %02d/%02d/20%02d\n",month,day,year);
		      // fprintf(stderr, "Link Quality = %c\n",link_quality);
		      // fprintf(stderr, "Latitude: %d %f' %c\n",lat_degrees,lat_minutes,lat_direction);
		      // fprintf(stderr, "Longitude: %d %f' %c\n",lon_degrees,lon_minutes,lon_direction);
	
		      sprintf(buf,"%02d%02d%02d%02d%02d.%02d",month,day,hours,minutes,year,seconds) ;
		      fprintf(fp1, "%s\n",buf2);
		      // fprintf(stderr, "got good acquisition\n");

		      // copy the new time and date to system and create "date mmddhhmmyy "
	
		      /* if caller passed -u at Command line */

		      if (update_datetime)  
			{
			  strcpy(buf2,mydate);
			  strcat(buf2,buf);
			  system(buf2);
			  system("hwclock -w -u");
			  system("hwclock -r");
			}

		      looper = 0; // quit program now we got one good $GPRMC
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

//can parse GNRMC sentence
int gps_get_position(char *sentence)
{
  int i;

  if(strncmp(sentence, "$GNRMC", 6) == 0)
    {
      strcpy(buf2,sentence);
      // fprintf(stderr, "Sentence = %s\n",buf2);
      //parse RMC sentence
      for(i = 0;i < 11;i++)
	{
	  sentence = strchr(sentence, ',');
	  if(sentence == NULL)
	    return -1;
	  sentence++; //first character in field
	  //pull out data
	  if(i == 0) // utc time
	    {
	      sscanf(sentence,"%2d %2d %2d",&hours,&minutes,&seconds) ;
	    }	
	  if(i == 1) //link quality
	    {
	      if(*sentence == 'A')
		link_quality = *sentence;
	      else
		link_quality = 'V';
	    }			
	  if(i == 2) //latitude
	    {
	      sscanf(sentence,"%2d %f",&lat_degrees,&lat_minutes) ;
	    }
	  if(i == 3) //lat direction
	    {
	      lat_direction = *sentence;
	    }
	  if(i == 4) // longitude
	    {	
	      sscanf(sentence,"%3d %f",&lon_degrees,&lon_minutes) ;
	    }
	  if(i == 5) //lon direction
	    {
	      lon_direction = *sentence;
	    }
	  if(i == 8) // utc date
	    {
	      sscanf(sentence,"%2d %2d %2d",&day,&month,&year) ;
	    }
	}
    }
  else
    {
      return -1; //unknown sentence type
    }
  return 0;	
}
