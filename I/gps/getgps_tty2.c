// added file pointer close on error exit ie timeouts
// changed for port 2
// moved storage to /var from /mnt RR 11/18/08 @ rose bay
/*
$Id: getgps_tty1.c 15751 2009-10-08 22:23:05Z tharan $
$Log: getgps_tty1.c,v $
Revision 1.2  2009/08/21 23:38:24  tharan
Added $Log$ to header.
Changed mydate from char[20] to char *.
Removed extraneous string_pos-- when replacing \r or \n with \0 in
sentence.
Added seconds when setting the date.

*/
// increased scan time to ~10 minutes from 30secs RR 10/04/09 @ rose bay
// this to allow for GPS that has been off all winter...ie Wx7  
//
// Nov 16 2009 Terry Haran
// Merged with Ronald Ross' amigos2-11072009 code.

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>

#define BAUDRATE B4800 // for GARMIN GPS 
#define SERIALPORT "/dev/ttyS2"
#define FILEOPEN1 "gpstime"
#define FILEOPEN2 "gpsdata"

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

main(int argc, char **argv)
{

	FILE  *fp1, *fp2;

	char sentence[128];
	char buf[128] ;
	int input_char;
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
		printf ("YES datetime update\n");
		update_datetime = 1;
		}
	else
		{
		printf ("NO datetime update\n");
		update_datetime = 0;
		}
      
	  /* open files for writing */
          fp1 = fopen("/var/gpstime","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
		system("/mnt/gpio/gps_OFF");
          exit (-1);
          }

	  fp2 = fopen("/var/gpsdata","a");
          if (fp2 < 0)
          {
		system("/mnt/gpio/gps_OFF");
          perror(FILEOPEN2);
          exit (-1);
          }

          /* first open the serial port for reading and writing */
                                                                  
          fd = open(SERIALPORT, O_RDWR | O_NDELAY ); 

          if (fd < 0) 
          {
            perror(SERIALPORT); 
	    system("/mnt/gpio/gps_OFF");
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
	printf("timeout in $GPRMC sync\n") ;
	fprintf(fp1,"TIMEOUT in $GPRMC Sync\n") ;
	fprintf(fp2,"TIMEOUT in $GPRMC Sync\n") ; 
	looper = 1;
	system("/mnt/gpio/gps_OFF");

 /* restore the old port settings before quitting */
       
	tcsetattr(fd,TCSANOW,&oldtio);

	fclose(fp1);
	fclose(fp2);
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
  	        // printf("%s\n",sentence);
	        // printf("out of grab characters\n"); // debug only

if(gps_get_position(sentence) == 0)
			{
	if (link_quality == 'A')
	{ 
	printf("Time: %02d:%02d:%02d\n",hours,minutes,seconds);
	// printf("Date: %02d/%02d/20%02d\n",month,day,year);
	// printf("Link Quality = %c\n",link_quality);
	// printf("Latitude: %d %f' %c\n",lat_degrees,lat_minutes,lat_direction);
	// printf("Longitude: %d %f' %c\n",lon_degrees,lon_minutes,lon_direction);
	
// first copy current file to backup file
	system("cp /var/gpsdata /var/oldgpsdata");
	
	sprintf(buf,"%02d%02d%02d%02d%02d.%02d",month,day,hours,minutes,year,seconds) ;
        fprintf(fp1,"%s\n",buf) ;
        fprintf(fp2,"%s\n",buf2) ;

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
	printf("Invalid Fix\n");
		}
        string_pos = 0;
        t = res;
        	}
        }
	looper--;
       }
  
          /* restore the old port settings before quitting */

          tcsetattr(fd,TCSANOW,&oldtio);

printf("Sentence = %s\n",sentence);
printf("looper = %d\n",looper);

	fclose(fp1);
	fclose(fp2);
	close(fd);

// update the copy of /mnt/gps files on /var
//	system("cp /mnt/gps/gpsdata /var/gpsdata");
//	system("cp /mnt/gps/gpstime /var/gpstime");

printf("all done now\n");
system("/mnt/gpio/gps_OFF");

}

//can parse GPRMC sentence
int gps_get_position(char *sentence)
{
	int i;

	if(strncmp(sentence, "$GPRMC", 6) == 0)
	{
        strcpy(buf2,sentence);
	// printf("Sentence = %s\n",buf2);
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
