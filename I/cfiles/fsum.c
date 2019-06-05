#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
  FILE *fp1;
  char ch1, same;
  unsigned int char_sum, two_byte_file_sum ;
  char_sum = two_byte_file_sum = 0;

  unsigned long l;

  if(argc!=2) {
    printf("Usage: must be one file <file 1>\n");
    exit(1);
  }

  /* open first file */
  if((fp1 = fopen(argv[1], "rb"))==NULL) {
    printf("Cannot open first file.\n");
    exit(1);
  }

  l = 0;
  same = 1;
  /* compare the files */
  while(!feof(fp1)) {
    ch1 = fgetc(fp1);
    if(ferror(fp1)) {
      printf("Error reading first file.\n");
      exit(1);
    }
    char_sum += (unsigned int)ch1 ;
    l++;
    printf("Sum number = %4d, Current char = %2x, Sum of file so far = %5x\n",l,ch1, char_sum);
  }
	l = l -1 ; // reduce the total chars due to l++
      char_sum = char_sum - 0xff ; // need to remove the EOF
      two_byte_file_sum = char_sum & 0xffff ;
      printf("Total chars = %4d, Sum of all chars in file = %5x, two_byte_sum = %4x, \n",l,char_sum, two_byte_file_sum);

  if(fclose( fp1 ) == EOF) {
    printf("Error closing file.\n");
    exit(1);
  }
  
  return 0;
}

