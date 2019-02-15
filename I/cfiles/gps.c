#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>

// #define BAUDRATE B38400
#define BAUDRATE B4800 // for GARMIN GPS 
#define SERIALPORT "/dev/ttyS0"
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
	char timeout ;
        
main()
        {

	FILE *fopen(), *fp1, *fp2;

	char sentence[128];
	char buf[128] ;
	int input_char;
	int string_pos;
        string_pos = 0;
        char t;
         
          int fd,c, res, looper;

          struct termios oldtio; /* will be used to save old port settings */
          struct termios newtio; /* will be used for new port settings */
          
	  /* open files for writing */
          fp1 = fopen("/mnt/gps/gpstime","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
          exit (-1);
          }

	  fp2 = fopen("/mnt/gps/gpsdata","a");
          if (fp2 < 0)
          {
          perror(FILEOPEN2);
          exit (-1);
          }

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
          newtio.c_cc[VTIME]    = 0;   /* inter-character timer unused */
          newtio.c_cc[VMIN]     = 0;   /* blocking read until first char received */
          
          tcflush(fd, TCIFLUSH);
          tcsetattr(fd,TCSANOW,&newtio);
          
          /* loop for input, reading 1-255 characters at a time until 'z' received */        

looper = 1100; // about one minute

          while (looper !=0) 
          {
	   timeout = 128;
           do	
           {
           res = read(fd,buf,255);   /* returns after at least 1 char has been input */
           timeout--;
           }
           while (buf[0] !='$' && string_pos == 0 && timeout !=0);  

if (timeout == 0)
{
printf("timeout in $ sync\n") ;
looper = 1;
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
                string_pos--;  
           	sentence[string_pos] = 0;  
  	     // printf("%s\n",sentence);
	     //	printf("out of grab characters\n"); // debug only

if(gps_get_position(sentence) == 0)
			{
	if (link_quality == 'A')
	{ 
	// printf("Time: %02d:%02d:%02d\n",hours,minutes,seconds);
	// printf("Date: %02d/%02d/20%02d\n",month,day,year);
	// printf("Link Quality = %c\n",link_quality);
	// printf("Latitude: %d %f' %c\n",lat_degrees,lat_minutes,lat_direction);
	// printf("Longitude: %d %f' %c\n",lon_degrees,lon_minutes,lon_direction);
	sprintf(buf,"%02d%02d%02d%02d%02d",month,day,hours,minutes,year) ;
        fprintf(fp1,"%s\n",buf) ;
        fprintf(fp2,"%s\n",buf2) ;
	looper = 1; // quit program now we got one good $GPRMC
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
 
printf("all done now\n");
fclose(fp1);
fclose(fp2);
       

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
