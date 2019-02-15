// 2010/01/13 Terry Haran
// getgps_tps_tty1.c derived from getps_alt_tty1.c
//
// 2010/01/15 Terry Haran
// First working version.
// Creates /var/tps containing at least 4 measurements
// at 30 second intervals.
//
// 2010/01/16 Terry Haran
// Increased measurement count to 40.
// Added timing of messages.
// Fixed bug in not printing last message.
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
#include <string.h>
#include <time.h>

#define BAUDRATE B115200 // default rate for grs GPS
#define FILEOPEN1 "/var/tps"
#define SERIALPORT "/dev/ttyS1"
#define SECONDS_PER_MEASUREMENT 30.0
#define MEASUREMENT_COUNT       40

#define BYTES_PER_MESSAGE 3000
#define BUFSIZE 4000

main()
{
  char buf[BUFSIZE];
  char *buf_ptr;
  int string_pos;
  string_pos = 0;
  char t;

  int fd;
  int msg_ctr;
  int bytes_read;
  int total;
  int total_total;
  int bytes_written;
  char *command;
  int command_length;
  unsigned long current_time_seconds;
  unsigned long target_time_seconds;
  long remain;
  long remain_old;
  long delta;

  FILE  *fp1;

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

  // send this command to disable sending D1 data
  while (write(fd,"dm,,/msg/jps/D1\r", 16) < 16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D1\n");

  // send this command to disable sending D2 data
  while (write(fd,"dm,,/msg/jps/D2\r", 16) < 16);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable D2\n");

  // send this command to disable GLONASS
  while (write(fd,"set,lock/glo/fcn,n\r", 19) < 19);
  // keep this message to serve as a delay
  fprintf(stderr, "After Serial port Write of disable GLONASS\n");

  // send this command to enable TPS binary messages
  sprintf(buf, "em,,def:{%.2f}&&em,,jps/ET:{%.2f}\r",
	  SECONDS_PER_MEASUREMENT, SECONDS_PER_MEASUREMENT);
  command_length = strlen(buf);
  while (write(fd, buf, command_length) != command_length);
  fprintf(stderr, "After Serial port Write of enable TPS:\n");
  fprintf(stderr, "%s\n", buf);

  // get current time
  current_time_seconds = time(NULL);
    SECONDS_PER_MEASUREMENT * (MEASUREMENT_COUNT + 1);
  remain = SECONDS_PER_MEASUREMENT * (MEASUREMENT_COUNT + 1);
  target_time_seconds = current_time_seconds + remain;

  total_total = 0;
  msg_ctr = 0;
  do
    {
      buf_ptr = buf;
      total = 0;
      remain_old = remain;
      do
	{
	  bytes_read = read(fd, buf_ptr, sizeof(buf) - (buf_ptr - buf));
	  if (bytes_read > 0)
	    {
	      buf_ptr += bytes_read;
	    }
	  total += bytes_read;
	  if (bytes_read < 0 || total >= sizeof(buf))
	    {
	      if (bytes_read < 0)
		{
		  perror("getgps_tps_tty1");
		  fprintf(stderr, "read error\n") ;
		  fprintf(fp1, "read error\n") ;
		}
	      else
		{
		  fprintf(stderr, "OVERRUN in TPS reading\n");
		  fprintf(fp1, "OVERRUN in TPS reading\n");
		}

	      /* restore the old port settings before quitting */
	      tcsetattr(fd,TCSANOW,&oldtio);
	      
	      fclose(fp1);
	      close(fd);
	      exit(-1);
	    }
	  current_time_seconds = time(NULL);
	  remain = (long)target_time_seconds -
	           (long)current_time_seconds;
	  delta = remain_old - remain;
	} while (delta < SECONDS_PER_MEASUREMENT &&
		 remain > 0 &&
		 total < BYTES_PER_MESSAGE);
      if (total > 0 || remain == 0)
	{
	  bytes_written = fwrite(buf, 1, total, fp1);
	  if (bytes_written != total)
	    {
	      perror("getgps_tps_tty1");
	      fprintf(stderr, "write error\n") ;
	      fprintf(fp1, "write error\n") ;

	      /* restore the old port settings before quitting */
	      tcsetattr(fd,TCSANOW,&oldtio);

	      fclose(fp1);
	      close(fd);
	      exit(-1) ;
	    }
	  fprintf(stderr, "msg_ctr: %2d  total: %4d  delta: %4d  remain: %4d\n",
		  ++msg_ctr, total, delta, remain);
	}
      total_total += total;
    } while(remain > 0);

  fprintf(stderr, "total_total: %d\n", total_total);
  
  /* restore the old port settings before quitting */
  tcsetattr(fd,TCSANOW,&oldtio);

  /* close files */
  fclose(fp1);
  close(fd);

  fprintf(stderr, "all done now\n");

  // end of main
}
