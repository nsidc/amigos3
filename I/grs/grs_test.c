// Nov 18th 2010 at Rose Bay
// test program for Ted while at Amigos2 on Scar

#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include<termios.h>
#include<stdio.h>
#include<string.h>
#include<time.h>        /* ctime, asctime      */

#define BAUDRATE B115200 // default rate for grs GPS
#define SERIALPORT "/dev/ttyS1"

#define CINBUFSIZE 127
#define COUTBUFSIZE 127

    struct tm *l_time;
        char string[100];
    FILE  *fp1;

    char sentence[100];
    char buf[100] ;
    char t ;
    int string_pos;
          unsigned long timeout ;
          int fd, res;

    char str[ ] = "This is a simple string";

    int dir,dir_max,n,j;
    float speed,speed_max,temp,humidity,pressure,volts_heater,temp_heater,volts;
//     n=0; was here till compiler complained,now in main

main()
{

n=0;

          struct termios oldtio; /* will be used to save old port settings */
          struct termios newtio; /* will be used for new port settings */

    
          /* now open the serial port for reading and writing */
          fd = open(SERIALPORT, O_RDWR | O_NDELAY );

          if (fd<  0)
          {
            perror(SERIALPORT);
            exit(-1);
          }

          /* save current port settings */
          tcgetattr(fd,&oldtio);

          /* initialize the port settings structure to all zeros */
          bzero(&newtio, sizeof(newtio));

          /* then set the baud rate, handshaking and a few other settings */
          newtio.c_cflag = (CBAUD&  BAUDRATE);
      newtio.c_cflag |= (CSIZE&  CS8);
          newtio.c_cflag |= CREAD;

      newtio.c_lflag&= 0x0 ;
          newtio.c_iflag = newtio.c_oflag = newtio.c_lflag ;
      newtio.c_oflag = ONLRET;

          /* set input mode */
          newtio.c_lflag&= 0x0 ;

          // newtio.c_cc[VTIME]    = 0;   /* inter-character timer used */
          // newtio.c_cc[VMIN]     = 0;   /* will return after first char or timeout */

          tcflush(fd, TCIFLUSH);
          tcsetattr(fd,TCSANOW,&newtio);

// ################ begin of loop for input, reading 1-n characters at a time until '0R0; is received

// send this command to specify use of the external antenna
  while (write(fd,"set,/par/ant/rcv/inp,ext\r", 25)<  25);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of set external antenna\n");

  // send this command to disable all messages
  while (write(fd,"dm,/dev/ser/a\r", 14)<  14);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable all\n");

  // send this command to disable sending D1 data
  while (write(fd,"dm,,/msg/jps/D1\r", 16)<  16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D1\n");

  // send this command to disable sending D2 data
  while (write(fd,"dm,,/msg/jps/D2\r", 16)<  16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D2\n");

  // send this command to enable GLONASS
  while (write(fd,"set,lock/glo/fcn,y\r", 19)<  19);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of enable GLONASS\n");

  // send this command to enable GNRMC messages
  while (write(fd,"em,,/msg/nmea/RMC\r",28)<  28);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of enable RMC\n");

// ################ first look for a LF to synchronize then read characters until a CR is received


j = 20 ;
do
{
timeout = 8000000;   
do
{
            string_pos = 0;
            do   
            {
    res = read(fd,buf,1);   /* returns after at least 1 char has been input */
                 timeout--;
            }
            while (buf[0] !='\n'&&  string_pos == 0&&  timeout !=0);

    if (timeout == 0)
    print_timeout();
           
    printf("Got LF\n");

// ####################################### end of looking for LF sync portion

            do   
            {
    res = read(fd,buf,1);   /* returns after at least 1 char has been input */
        if(res)
                    {
                    sentence[string_pos++] = buf[0] ;
                    }
                 timeout--;
            }
            while (buf[0] !='\r'&&  timeout !=0);
            sentence[string_pos] = 0;

    if (timeout == 0)
    print_timeout();

    printf("Got CR\n");
    printf(" Sentence = %s\n",sentence) ;
    j-- ;
}
while (j>  0);

// ####################################### end of looking for CR sync portion

}
while (1);

// ####################################### if we have a timeout

    if (timeout == 0)
    print_timeout();

// ####################################### store data in 1 file

// #######################################                

    /* restore the old port settings before quitting */
    tcsetattr(fd,TCSANOW,&oldtio);

    /* close files */   
    // fclose(fp1);
    close(fd);

    printf("all done now\n");

// end of main
}

int print_timeout()
{
        printf("timeout in TRACE sync @ %s\n",string) ;
        close(fd);
        exit(-1) ;   
}

