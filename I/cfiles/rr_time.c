
/* 
A modified version of devmem.c to support I2C i/o
written RR 08/06/05
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include <ctype.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/mman.h>
/************************************************************************
 *
 * Purpose: To play with the time.h functions.
 *
 * Author:  M.J. Leslie
 *
 * Date:    18-Mar-95
 *
 ************************************************************************/

#include <time.h>		        /* ctime, asctime      */

main()
{
  time_t now;				/* define 'now'. time_t is probably
					 * a typedef	*/

				        /* Calender time is the number of 
				         * seconds since 1/1/1970   	*/

  now = time((time_t *)NULL);		/* Get the system time and put it
   					 * into 'now' as 'calender time' */

  printf("%s", ctime(&now));		/* Format data in 'now'
					 * NOTE that 'ctime' inserts a
					 * '\n' */ 


  {
    struct tm *l_time;
    char string[20];
					 
    time(&now);
    l_time = localtime(&now);
    strftime(string, sizeof string, "%m%d%y %H:%M:%S\n", l_time);
    printf("%s", string);
  }


}
