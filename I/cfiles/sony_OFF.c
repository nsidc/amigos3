/*
*
A modified version of devmem.c
*
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

#define GPDR0 0x40e0000c
#define GPDR1 0x40e00010
#define GPDR2 0x40e00014
#define GPSR0 0x40e00018
#define GPSR1 0x40e0001c
#define GPSR2 0x40e00020
#define GPCR0 0x40e00024
#define GPCR1 0x40e00028
#define GPCR2 0x40e0002c

#define GAFR0_L 0x40e00054
#define GAFRO_U 0x40e00058
#define GAFR1_L 0x40e0005c
#define GAFR1_U 0x40e00060
#define GAFR2_L 0x40e00064
#define GAFR2_U 0x40e00068

  
#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
  __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)
 
#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)

int main() {
    int fd, loop;
    void *map_base, *virt_addr; 
	unsigned long read_result, writeval;
	off_t target;
	int access_type = 'h';

    if((fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
    // printf("/dev/mem opened target 1.\n"); 
    fflush(stdout);


/* reset GPIO61 Sony_ON*/

target = GPCR1 ;

	// printf("target_reg is 0x%X \n", target);
    
/* Map one page */
    
	map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    	// printf("Memory mapped at address %p.\n", map_base); 
    	fflush(stdout);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x20000000 to reset Sony_ON (GPIO61) */
	read_result = read_result | 0x20000000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);
        
    close(fd);
    return 0;
}
