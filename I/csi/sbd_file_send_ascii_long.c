// /mnt/csi/sbd_file_send_ascii_long.c
// Terry Haran 2009/12/16
// Derived from /mnt/weather/sbd_file_send_ascii.c
//
// Read an array of arbitrary length.
// Assume that the array consists of the following space delimited fields:
//   stationID arrayID date time field1 field2 .. fieldN
// where each field has a maximum length of 10 characters.
// Break the array up into a series of messages consisting of:
//   stationID arrayID0 date time field1 field2 .. fieldM1
//   stationID arrayID1 date time fieldM1+1 fieldM1+2 ... fieldM2
//     etc. with the last message:
//   stationID arrayIDk date time fieldMk+1 fieldMk+2 ... fieldN
//   
// Each message will be less than or equal to 116 characters.
// Each message will not break in the middle of a field.
// Write each message to file /var/foo_long.
// Call /mnt/weather/sbd_file_send_ascii /var/foo_from_long for each message.

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>

#define MAXMSGSIZE     114

void write_message(unsigned char *buf, int bytes_to_output)
{
  FILE *fp_out;

  if ((fp_out = fopen("/var/foo_from_long", "w")) == NULL) {
    printf("Cannot open output file.\n");
    exit(1);
  }

  if (fwrite(buf, 1, bytes_to_output, fp_out) != bytes_to_output) {
    printf("Error writing to file.\n");
    exit(1);
  }

  fclose(fp_out);

  system("/mnt/weather/sbd_file_send_ascii /var/foo_from_long");
}


int main(int argc, char *argv[]) 
{
  FILE *fp_in;
  FILE *fp_out;
  unsigned char c;
  unsigned char buf[MAXMSGSIZE+1];
  unsigned char *in_ptr;
  unsigned char *out_ptr;
  unsigned char *end_of_last_field_ptr;
  unsigned char *end_of_second_field_ptr;
  unsigned char *end_of_fourth_field_ptr;
  int bytes_to_output;
  int waiting_for_blank;
  int field_ctr;
  int msg_ctr;

  printf("Executing %s %s\n", argv[0], argv[1]);
	
  if(argc!=2) {
    printf("Usage: must specify file\n");
    exit(1);
  }
	
  /* open input file */
  if((fp_in = fopen(argv[1], "r"))==NULL) {
    printf("Cannot open input file\n");
    exit(1);
  }

  in_ptr = buf;
  end_of_last_field_ptr = buf;
  end_of_second_field_ptr = buf;
  end_of_fourth_field_ptr = buf;
  waiting_for_blank = 0;
  field_ctr = 0;
  msg_ctr = 0;

  while(!feof(fp_in)) {
    c = fgetc(fp_in);
    if(ferror(fp_in)) {
      printf("Error reading from file.\n");
      exit(1);
    }

    *in_ptr++ = c;
    if (in_ptr == buf + MAXMSGSIZE) {
      *(end_of_last_field_ptr - 1) = '\n';
      bytes_to_output = end_of_last_field_ptr - buf;
      write_message(buf, bytes_to_output);
      for (in_ptr = end_of_last_field_ptr,
	   out_ptr = end_of_fourth_field_ptr;
	   in_ptr < buf + MAXMSGSIZE;
	   *out_ptr++ = *in_ptr++) {
      }
      in_ptr = out_ptr;
      *end_of_second_field_ptr = '0' + msg_ctr++;
      end_of_last_field_ptr = end_of_fourth_field_ptr;
    }

    if (c == ' ') {
      if (waiting_for_blank) {
	waiting_for_blank = 0;
	end_of_last_field_ptr = in_ptr;
	if (field_ctr == 2) {
	  in_ptr--;
	  end_of_second_field_ptr = in_ptr++;
	  *end_of_second_field_ptr = '0' + msg_ctr++;
	  *in_ptr++ = c;
	}
	if (field_ctr == 4)
	  end_of_fourth_field_ptr = in_ptr;
      }
    } else {
      if (!waiting_for_blank) {
	waiting_for_blank = 1;
	field_ctr++;
      }
    }
  }

  bytes_to_output = in_ptr - buf - 1;
  write_message(buf, bytes_to_output);
  fclose(fp_in);
}
