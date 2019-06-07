
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
#include <math.h>
#include <float.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/mman.h>

#include <time.h>		        /* ctime, asctime      */

#include <sys/syscall.h>

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

#define GPLR0 0x40e00000
#define GPLR1 0x40e00004
#define GPLR2 0x40e00008

#define PGSR0 0x40f00020
#define PGSR1 0x40f00024
#define PGSR2 0x40f00028

#define SDA_bit 0x001000 
#define SCL_bit 0x000800
#define DQ_bit 0x04000000

#define READ_ROM 0x33
#define SKIP_ROM 0xCC
#define CONVERT_Temp  0x44
#define CONVERT_Voltage 0xB4
#define RECALL_Memory 0xB8
#define RECALL_PAGE00 0x00
#define READ_SCRATCH_PAD 0xBE
#define COPY_SCRATCH_PAD 0x48
#define READ_PAGE00 0x00
#define WRITE_SP 0x4E
#define SP_00 0x00
#define ICA 0x1



  
#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
  __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)


#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)

#define FILEOPEN1 "voltage"
#define FILEOPEN2 "voltagedata"

/*
'------------
' This module is a collection of low level I2C routines intended to be
' included in a project using such I2C devices as the Microchip 24 series 
' EEPROMs, MAX518 D/A, PCF8574 I/O Expander, DS1803 Digital Pot, PCF8591
' A/D plus D/A and many other devices.

' I2C_out_byte(u8 O_byte) - sends O_byte to I2C
' slave, most significant bit first.
'
' I2C_nack() - provides high Z on SDA for one clock pulse
' allowing slave to acknowledge receipt of a byte.
'
' I2C_in_byte(u8 I_byte) - receives a byte from I2C
' slave.
'
' I2C_ack() - send ack to slave by bringing SDA low for one 
' clock pulse.
'
' I2C_start() - initiates sequence by bringing SDA low while 
' SCL is high.  (Could be Private rather than Public).
'
' I2C_stop() - terminates sequence by bringing SDA high 
' while SCL is high. (Could be Private rather than Public).
'
' I2C_high_SDA() - bring SDA high (high Z)
'
' I2C_high_SCL() - bring SCL high (high Z)  
'
' I2C_low_SDA() - bring SDA low, hard logic zero
'
' I2C_low_SCL() - bring SCL low, hard logic zero
'
' Copyright, Peter H. Anderson, Baltimore, MD, Sept, '99
'
*/

	int fd;
	void *map_base, *virt_addr; 
	float avg_voltage , avg_current;
	int A,B,C,D,E,F,G,H,I,J;
	off_t target;
	unsigned long read_result;

	float avg_temperature, float_temperature , tilt;
	int average_count ;

int main() 
{


A = 3; // was 3 or 3us
B = 360;
C = 300;
D = 63; 
E = 1; 
F = 360; // was 360
G = 1;
H = 485 * 3;
I = 60 * 3;
J = 250 * 3;


	struct tm *l_time;
    	char string[20];

    	if((fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
    	// printf("/dev/mem opened target 1.\n"); 
    	fflush(stdout);
	
	FILE  *fp1, *fp2;

	/* open files for writing */
          fp1 = fopen("/mnt/i2c/voltage","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
          exit (-1);
          }

	  fp2 = fopen("/mnt/i2c/voltagedata","a");
          if (fp2 < 0)
          {
          perror(FILEOPEN2);
          exit (-1);
          }


init_gpio() ;
// get_i2c_data() ;
get_i2c_data_temp() ;

time_t now;				/* define 'now'. time_t is probably
					 * a typedef	*/

    time(&now);
    l_time = localtime(&now);
    strftime(string, sizeof string, "%m/%d/%y %H:%M:%S\n", l_time);
//    printf("%s", string);

//printf("Input voltage = %03x.3fV\n", avg_voltage );
//printf("Input current = %03x.3fA\n", avg_current );
// printf("PCB temperature = %03x.3fC\n", avg_temperature );
	
	fprintf(fp1,"%03.3f V %03.3f A %03.3f C %s ",avg_voltage, avg_current,avg_temperature,string) ;
        fprintf(fp2,"%03.3f V %03.3f A %03.3f C %s",avg_voltage, avg_current,avg_temperature,string) ;

	fclose(fp1);
	fclose(fp2);
	close(fd);

	system("cp /mnt/i2c/voltage /var/voltage");

	system("cp /mnt/i2c/voltagedata /var/voltagedata");

	return 0;

}


/* ********************************************************************** */
/*
Public Sub I2C_in_byte(ByRef I_byte As Byte) 
   DIM N as Byte, Y as Byte 
   I_byte = 0
   For N = 1 to 8 Step 1
      Call I2C_high_SCL()       ' bring clock high
      Y =  GetPin(SDA)      ' read SDA
      Call I2C_low_SCL()
      I_byte = I_byte * 2 + Y   ' shift left and insert Y
   Next 
	Call ReadAck		
End Sub
*/
/* ********************************************************************** */
unsigned long I2C_in_byte_rr() 
{
	
	unsigned long read_result ;
	char n;
	unsigned long in_byte ; 
	in_byte = 0;

        for (n=1; n<9;n++) 
	{
	I2C_high_SCL();		// bring clock high
        
	/* for GPDR 0 = input and 1 = output */
	/* make this an input to read */

	virt_addr = map_base + (GPDR2 & MAP_MASK) ;
    	read_result = *((unsigned long *) virt_addr) ;
	*((unsigned long *) virt_addr) = (read_result & ~SDA_bit) ;

	virt_addr = map_base + (GPLR2 & MAP_MASK) ;
    	read_result = (*((unsigned long *) virt_addr))  & SDA_bit ; // finally read SDA

        if (read_result==0)
        read_result=0;
        else
        read_result=1;

	I2C_low_SCL();
        in_byte = (in_byte * 2) + read_result ;   // shift left and insert SDA bit
        } 
	return in_byte ;
	// Call SendAck()		
}
/* ********************************************************************** */
int I2C_out_byte(unsigned char out_byte)
{ 
   char n ;
   for (n=1; n<9;n++)
	{

	if (out_byte >= 128) 	// most sig bit is a one
	I2C_high_SDA();
	else
        I2C_low_SDA();     	// set SDA          


	I2C_high_SCL();		//Clock Pulse
	I2C_low_SCL();		//Clock Pulse

	out_byte = out_byte * 2 ;   // shift left      
   	} 
	if (ReadAck() == 0)  		// Reads the acknowledge from the slave device.	   
	return 0 ;
	else 
	return 1;

}
/* ********************************************************************** */
int ReadAck()            // allows slave to acknowledge  
{

int read_result ;

I2C_high_SDA();          // SDA high
tickDelay(100); // experiment rr saturday 7/08/06
I2C_high_SCL();          // and then clock
read_result = I2CReport() ; // Reports the status of the acknowledge condition.
tickDelay(10); // experiment rr saturday 7/08/06
I2C_low_SCL();

if (read_result==1)
return 1 ;
else
return 0;

}
/* ********************************************************************** */
int I2CReport()
{
	unsigned long read_result ;

/* for GPDR 0 = input and 1 = output */
/* make this an input */

	virt_addr = map_base + (GPDR2 & MAP_MASK) ;
    	read_result = *((unsigned long *) virt_addr) ;
	*((unsigned long *) virt_addr) = (read_result & ~SDA_bit) ;

	virt_addr = map_base + (GPLR2 & MAP_MASK) ;
    	read_result = (*((unsigned long *) virt_addr))  & SDA_bit ;
	
	if (read_result == 0){ 
	// printf("Acknowledge Received\n");
	return 0;
	}else{	
	printf("I2C Problem\n");
	return 1;
	}

}
/* ********************************************************************** */
int SendAck()            // send ack to slave by bringing SDA low
{
I2C_low_SDA();
I2C_high_SCL();
delay(1);
I2C_low_SCL();
I2C_high_SDA();          // be sure SDA is again high
}
/* ********************************************************************** */
int SendNAck()            // send nack to slave by bringing SCL low then SDA high
{   
I2C_low_SCL();
//I2C_low_SDA()
delay(1);
I2C_high_SDA();
delay(1);
I2C_high_SCL();          // be sure SCL and SDA are then high
}
/* ********************************************************************** */
int I2C_start()          // bring SDA low while SCL is high
{

// printf("in I2C_start\n");
   
// I2C_low_SCL()
I2C_high_SDA();
I2C_high_SCL();
I2C_low_SDA();
I2C_low_SCL();
}
/* ********************************************************************** */
int I2C_stop()           // bring SDA high while SCL is high
{

// printf("in I2C_stop\n");

I2C_low_SCL();
I2C_low_SDA();
I2C_high_SCL();
I2C_high_SDA();
}
/* ********************************************************************** */
int I2C_high_SDA()
{
unsigned long read_result ;

/* for GPDR 0 = input and 1 = output */

	virt_addr = map_base + (GPDR2 & MAP_MASK) ;
    	read_result = *((unsigned long *) virt_addr) ;
	*((unsigned long *) virt_addr) = (read_result & ~SDA_bit) ;

 // make input which will be pulled up by 10k resistor

tickDelay(24); // experiment rr sunday 6/25/06

}
/* ********************************************************************** */
int I2C_high_SCL()     
{
// printf("in I2C_high_SCL\n");

	virt_addr = map_base + (GPSR2 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = SCL_bit ; // make hard logic one

tickDelay(24); // experiment rr sunday 6/25/06

}
/* ********************************************************************** */
int I2C_low_SDA()
{
unsigned long read_result ;

/* first make sure this is an output */

	virt_addr = map_base + (GPCR2 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = SDA_bit ; // make hard logic zero

/* and make sure this is an output, since it may have been an input prior to this */
/* for GPDR 0 = input and 1 = output */	
	
	virt_addr = map_base + (GPDR2 & MAP_MASK) ;
    	read_result = *((unsigned long *) virt_addr) ;
	*((unsigned long *) virt_addr) = (read_result | SDA_bit) ;

tickDelay(24); // experiment rr sunday 6/25/06

}
/* ********************************************************************** */
int I2C_low_SCL()
{
// printf("in I2C_low_SCL\n");

	virt_addr = map_base + (GPCR2 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = SCL_bit ; // make hard logic zero

tickDelay(24); // experiment rr sunday 6/25/06

}
/* ********************************************************************** */
// int get_i2c_data()

/* ********************************************************************** */
int get_i2c_data_temp()
{
		
	int return_code, internal_register, config_register, temp_register ;
  
	
	config_register = 0 ;

	

   	printf("in tilt loop now --------------------- \n");

I2C_start() ; // read from the config register

// printf("first cycle\n");
   return_code = I2C_out_byte(0x9e) ; //DS1631 address is 0x90 + 0xE all bit high for now
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
// printf("second cycle\n"); 
   return_code = I2C_out_byte(0xAC) ; //target address of config register
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
I2C_start() ;

// printf("third cycle\n");
   return_code = I2C_out_byte(0x9f) ; //tell DS1631 we wish to read next
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);

// printf("seventh cycle\n");
   return_code = I2C_in_byte_rr() ;
   // if (return_code)
   	// printf("I2C_in_byte_rr_first returned: %d\n", return_code);

config_register = return_code ;
	printf("config_register = %x\n", return_code);

SendNAck();
I2C_stop() ;
 
I2C_start() ;
// printf("first cycle\n");
   return_code = I2C_out_byte(0x9e) ; //DS1631 address is 0x90 + 0xE all bit high for now
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
// printf("second cycle\n"); 
   return_code = I2C_out_byte(0x51) ; //DS1631 command byte to start a conversion
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
I2C_stop() ;

// wait for conversion
printf("allow time for temeprature conversion\n");
delay(100) ;
printf("time up\n");

 
I2C_start() ;
// printf("first cycle\n");
   return_code = I2C_out_byte(0x9e) ; //DS1631 address is 0x90 + 0xE all bit high for now
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
// printf("second cycle\n"); 
   return_code = I2C_out_byte(0xAA) ; //DS1631 command byte to read data back
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
I2C_start() ;

// printf("third cycle\n");
   return_code = I2C_out_byte(0x9f) ; //tell DS1631 we wish to read next
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);

// printf("seventh cycle\n");
   return_code = I2C_in_byte_rr() ;
   // if (return_code)
   	// printf("I2C_in_byte_rr_first returned: %d\n", return_code);

temp_register = return_code ;
	printf("temp_register = %x\n", return_code);

SendNAck();
I2C_stop() ;

}

int tickDelay(int dly)
{

// printf("in delay\n");

int t;
while (dly !=0)
	{
	for (t=0;t<7;t++); // was org 7
	dly--;
	}
}
/* ********************************************************************** */
int delay(int dly)
{

// printf("in delay\n");

int t;
while (dly !=0)
	{
	for (t=0;t<10000;t++);
	dly--;
	}
}

/* ********************************************************************** */
int init_gpio()
{

/* We need to set GPIO 26 to an outputs, that means first setting high these bit in
 setting in GPSR0 */

target = GPSR0 ;

	// printf("target GPSR0 is 0x%X \n", target);
    
/* Map one page, only need to get this once (I hope!)  */
    
	map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    	// printf("Memory mapped at address %p.\n", map_base); 
    	fflush(stdout);
    	read_result = 0;
    	virt_addr = map_base + (target & MAP_MASK);
    
/*  OR this with 0x04000000 to set output high for GPIO 26 */
	read_result = read_result | DQ_bit ;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);
        
/* now set direction of pin GPIO 26 */

target = GPDR0 ;

	// printf("target GPDR0 is 0x%X \n", target);

	virt_addr = map_base + (target & MAP_MASK);
	read_result = 0;
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x04000000 to set outputs high for GPIO 26 */
	read_result = read_result | DQ_bit ;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	// printf("read_result after write is 0x%X \n", read_result);


/* We need to set GPIO 75 and 76 to outputs, that means first setting high these bit in
 setting in GPSR2 */

target = GPSR2 ;

	// printf("target GPSR2 is 0x%X \n", target);
    
/* Map one page, only need to get this once (I hope!)  */
    
	map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    	// printf("Memory mapped at address %p.\n", map_base); 
    	fflush(stdout);
    
    	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x001800 to set outputs high for GPIO 75 & 76 */
	read_result = read_result | SDA_bit | SCL_bit ;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);
        
/* now set direction of pins GPIO 75 and 76 */

target = GPDR2 ;

	// printf("target GPDR2 is 0x%X \n", target);

	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	// printf("read_result before masking is 0x%X \n", read_result);
/*  OR this with 0x001800 to set outputs high for GPIO 75 & 76 */
	read_result = read_result | SDA_bit | SCL_bit ;
  
	// printf("read_result after masking after read is 0x%X \n", read_result);
	*((unsigned long *) virt_addr) = read_result;
    
	read_result = *((unsigned long *) virt_addr);
	// printf("read_result after write is 0x%X \n", read_result);

}

