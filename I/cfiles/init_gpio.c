/* 
A modified version of devmem.c
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
#define GAFR0_U 0x40e00058
#define GAFR1_L 0x40e0005c
#define GAFR1_U 0x40e00060
#define GAFR2_L 0x40e00064
#define GAFR2_U 0x40e00068

#define PGSR0 0x40f00020
#define PGSR1 0x40f00024
#define PGSR2 0x40f00028

  
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
	
	target = GAFR0_U ;
	map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    	// printf("Memory mapped at address %p.\n", map_base); 
    	fflush(stdout);

// **************************************************************************
	/* set bits 23-26 to 00, to regular GPIO */
target = GAFR0_U ;

map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);

	// printf("target GAFR0_U is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  AND this with 0x to make GPIO23-26 */
	read_result = read_result & 0xffc03fff;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
	/* set bits 58-63 to 00, to regular GPIO */
target = GAFR1_U ;

	// printf("target GAFR1_U is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  AND this with 0x to make GPIO58-63 */
	read_result = read_result & 0x000fffff;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
	/* set bits 64-77 to 00, to regular GPIO */
target = GAFR2_L ;

	// printf("target GAFR2_L is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  AND this with 0x to make GPIO64-77 */
	read_result = read_result & 0xc0000000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************

// printf("Here after GAFR register set\n"); 

/* We need to set GPIO's 23-26 and 58-77 low, that means reseting in GPCR0, GPCR1 & GPCR2 */

// **************************************************************************
target = GPCR0 ; // GPIO's 23-26

	// printf("target GPCR0 is 0x%X \n", target);
    
  	read_result = 0 ;
    
    	virt_addr = map_base + (target & MAP_MASK);
    	// read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x07800000 to make outputs of GPIO23-26 */
	read_result = read_result | 0x07800000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	// read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);


// **************************************************************************     
target = GPCR1 ; // GPIO's 58-63

	// printf("target GPCR1 is 0x%X \n", target);
	
	read_result = 0 ;

    	virt_addr = map_base + (target & MAP_MASK);
    	// read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0xfc000000 to make outputs of GPIO58-63 */
	read_result = read_result | 0xfc000000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	// read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);
        

// **************************************************************************
target = GPCR2 ; // GPIO's 64-77

	read_result = 0 ;

	// printf("target GPCR2 is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	// read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x0003ffff to make outputs of GPIO64-77 */
	read_result = read_result | 0x0003fff;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	// read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);
       
// **************************************************************************
target = GPSR0 ; // need to set CF_RESET and CF_ON = 1 

	// printf("target GPSR0 is 0x%X \n", target);
    
  	read_result = 0 ;
    
    	virt_addr = map_base + (target & MAP_MASK);
    	// read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x02800000 to make high the outputs of GPIO23 & 25 */
	read_result = read_result | 0x02800000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	// read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
target = GPSR1 ; // need to set RS232_ON 

	read_result = 0 ;

	// printf("target GPSR1 is 0x%X \n", target); 
 
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  set GPSR1 to 0x04000000 ie high on GPIO58 */
	read_result = 0x04000000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
target = GPSR2 ; // need to set NO_SLEEP

	read_result = 0 ;

	// printf("target GPSR2 is 0x%X \n", target);

    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  set GPSR2 to 0x00400 ie high on GPIO74 */
	read_result = 0x00400;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
// printf("Here after SET and RESET before DDR's \n"); 
// **************************************************************************
target = GPDR0 ;

	// printf("target GPDR0 is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x07800000 to make GPIO23-26 outputs of GPIO 00-31 */
	read_result = read_result | 0x07800000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
target = GPDR1 ;

	// printf("target GPDR1 is 0x%X \n", target);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0xfc000000 to make outputs of GPIO58-63 */
	read_result = read_result | 0xfc000000;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************
target = GPDR2 ;

	// printf("target GPDR2 is 0x%X \n", target);
      
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x00003fff to make outputs of GPIO64-77 */
	read_result = read_result | 0x00003fff;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

// **************************************************************************   
target = PGSR0 ;

	// printf("target PGSR0 is 0x%X \n", target);

// THIS REMAP is needed as address switched from registers 40e0 to 40f0
 
map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    
    	virt_addr = map_base + (target & MAP_MASK);
	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x02800000 to make sleep bits high for output of GPIO23 & 25 */
	 read_result = read_result | 0x02800000;
	*((unsigned long *) virt_addr) = read_result;

/* now get the result and AND with the bit that need to be reset low */
	read_result = *((unsigned long *) virt_addr);

	// printf("read_result of PGSR0 before write is 0x%X \n", read_result);

/* AND this with 0xfaffffff to make sleep bits low for outputs of GPIO24 & 26 */
	read_result = read_result & 0xfaffffff;
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result of PGSR0 after write is 0x%X \n", read_result);

// **************************************************************************        
target = PGSR1 ;

	// printf("target PGSR1 is 0x%X \n", target);
      
    	virt_addr = map_base + (target & MAP_MASK);

	// printf("read_result before masking is 0x%X \n", read_result);
// make all GPIOs 58-63 low during sleep
	read_result = *((unsigned long *) virt_addr);
/*  AND this with 0x03ffffff to make sleep bits low for outputs of GPIO58-63 */
	read_result = read_result & 0x03ffffff; 
	*((unsigned long *) virt_addr) = read_result;

// ************************************************************************** 
target = PGSR2 ;

	// printf("target PGSR2 is 0x%X \n", target);  
  
    	virt_addr = map_base + (target & MAP_MASK);

	// printf("read_result before masking is 0x%X \n", read_result);
// make all GPIOs 64-77 low during sleep
	read_result = *((unsigned long *) virt_addr);
/*  AND this with 0x1fc000 to make sleep bits low for outputs of GPIO64-77 */
	read_result = read_result & 0x1fc000; 
	*((unsigned long *) virt_addr) = read_result;
   

    close(fd);
    printf("init_gpio done \n");
    return 0;
}
