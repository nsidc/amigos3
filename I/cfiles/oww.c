
/* 
A modified version for one wire devices to support DS2438 
written RR 09/11/05

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

#define DQ_bit 0x04000000
  
#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
  __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)


#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)

#define FILEOPEN1 "voltage"
#define FILEOPEN2 "voltagedata"

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

	int fd ;
	void *map_base, *virt_addr ; 
	float avg_voltage , avg_current, avg_temperature, resolution ;
	float float_voltage , float_current, float_temperature ;
	int voltage, current, temperature, scratch ;
	unsigned long read_result, status_config ;
	int A,B,C,D,E,F,G,H,I,J;
        off_t target;
	int avgloop, average_count ;

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

average_count = 10 ;

	FILE  *fp1, *fp2;

	struct tm *l_time;
    	char string[20];
	
	/* open files for writing */
          fp1 = fopen("/mnt/oww/voltage","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
          exit (-1);
          }

	  fp2 = fopen("/mnt/oww/voltagedata","a");
          if (fp2 < 0)
          {
          perror(FILEOPEN2);
          exit (-1);
          }


	if ((fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
    	// printf("/dev/mem opened target 1.\n"); 
    	fflush(stdout);
	
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

// this first go round is just a primer, tossed away

OWReadTemp_Volts_Current();

avg_voltage = avg_current = avg_temperature = 0 ;

for (avgloop = 0; avgloop < average_count ; avgloop++)
	{
	OWReadTemp_Volts_Current();
	avg_voltage = avg_voltage + float_voltage;
	avg_current = avg_current + float_current;
	avg_temperature = avg_temperature + float_temperature;
	}

avg_voltage 	= avg_voltage / average_count ;
avg_current 	= avg_current / average_count ;
avg_temperature = avg_temperature / average_count ;

time_t now;				/* define 'now'. time_t is probably
					 * a typedef	*/

    time(&now);
    l_time = localtime(&now);
    strftime(string, sizeof string, "%m/%d/%y %H:%M:%S\n", l_time);
    printf("%s", string);

printf("Input voltage 	= %.3f V\n", avg_voltage );
printf("Input current 	= %.3f A\n", avg_current );
printf("PCB Temperature = %.3f C\n", avg_temperature);
	
	fprintf(fp1,"%.3f V %.3f A %.3f C %s",avg_voltage, avg_current, avg_temperature, string) ;
      fprintf(fp2,"%.3f V %.3f A %.3f C %s",avg_voltage, avg_current, avg_temperature, string) ;

	fclose(fp1);
	fclose(fp2);
	close(fd);

	system("cp /mnt/i2c/voltage /var/voltage");
	system("cp /mnt/i2c/voltagedata /var/voltagedata");
	return 0;

}


/* ********************************************************************** */
int OWW_input()
{
	unsigned long read_result ;

/* for GPDR 0 = input and 1 = output */
/* make this an input */

	virt_addr = map_base + (GPDR0 & MAP_MASK) ;
    	read_result = *((unsigned long *) virt_addr) ;
	*((unsigned long *) virt_addr) = (read_result & ~DQ_bit) ;

	virt_addr = map_base + (GPLR0 & MAP_MASK) ;
    	read_result = (*((unsigned long *) virt_addr))  & DQ_bit ;
	
	if (read_result == 0){ 
	// printf("Received\n");
	return 0;
	}else{	
	// printf("OWW Problem\n");
	return 1;
	}

}

/* ********************************************************************** */
int OWW_out_high()     
{
// printf("in 1wire drive high\n");

	target = GPDR0 ;

	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	read_result = read_result | DQ_bit ;
  
	*((unsigned long *) virt_addr) = read_result;
    
	virt_addr = map_base + (GPSR0 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = DQ_bit ; // make hard logic one
}
/* ********************************************************************** */
int OWW_out_low()
{
// printf("in 1Wire drive low\n");
target = GPDR0 ;

	virt_addr = map_base + (target & MAP_MASK);
    	read_result = *((unsigned long *) virt_addr);

	read_result = read_result | DQ_bit ;
  
	*((unsigned long *) virt_addr) = read_result;

	virt_addr = map_base + (GPCR0 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = DQ_bit ; // make hard logic zero
}

/* ********************************************************************** */
// Generate a 1-Wire reset, return 1 if no presence detect was found,
// return 0 otherwise.
//
int OWTouchReset(void)
{
int result;
	
tickDelay(G);
	OWW_out_low(); // Drives DQ low
tickDelay(H);
	OWW_out_high(); // Releases the bus
tickDelay(I);
	result = OWW_input() & 0x1; // Sample for presence pulse from slave
tickDelay(J); // Complete the reset sequence recovery

	return result; // Return sample presence pulse result
}
/* ********************************************************************** */
// Send a 1-Wire write bit. Provide 10us recovery time.
//
int OWWriteBit(int bit)
{

	if (bit)
	{
	// Write '1' bit
		OWW_out_low(); // Drives DQ low
	tickDelay(A);
		OWW_out_high(); // Releases the bus
	tickDelay(B); // Complete the time slot and 10us recovery
	}
	else
	{
	// Write '0' bit
		OWW_out_low(); // Drives DQ low
	tickDelay(C);
		OWW_out_high(); // Releases the bus
	tickDelay(D);
	}
}
/* ********************************************************************** */
// Read a bit from the 1-Wire bus and return it. Provide 10us recovery time.

int OWReadBit(void)
{
	int result;
	OWW_out_low(); // Drives DQ low
tickDelay(A);
	OWW_out_high(); // Releases the bus
tickDelay(E);
	result = OWW_input() & 0x1; // Sample the bit value from the slave
tickDelay(F); // Complete the time slot and 10us recovery

return result;
}
/* ********************************************************************** */
// Write 1-Wire data byte
//
int OWWriteByte(int data)
{
	int loop;

// Loop to write each bit in the byte, LS-bit first
	for (loop = 0; loop < 8; loop++)
	{
	OWWriteBit(data & 0x1);
// shift the data byte for the next bit
	data >>= 1;
	}
}
/* ********************************************************************** */
// Read 1-Wire data byte and return it
//
int OWReadByte(void)
	{
	int loop; 
	int result=0;
	for (loop = 0; loop < 8; loop++)
	{
	// shift the result to get it ready for the next bit
	result >>= 1;
	// if result is one, then set MS bit
	if( OWReadBit() )
		{
		result |= 0x80;
		}
	}
	return result;
}
/* ********************************************************************** */
// Write a 1-Wire data byte and return the sampled result.
//
int OWTouchByte(int data)
{
	int loop, result=0;
	
	for (loop = 0; loop < 8; loop++)
	{
	// shift the result to get it ready for the next bit
	result >>= 1;
	// If sending a '1' then read a bit else write a '0'

	if (data & 0x01)
	{
		if (OWReadBit())
		result |= 0x80;
	}
	else
		OWWriteBit(0);
		// shift the data byte for the next bit
		data >>= 1;
	}
return result;
}
/* ********************************************************************** */
// Write a block 1-Wire data bytes and return the sampled result in the same
// buffer.
//
void OWBlock(unsigned char *data, int data_len)
{
	int loop;

	for (loop = 0; loop < data_len; loop++)
	{
	data[loop] = OWTouchByte(data[loop]);
	}
}
/* ********************************************************************** */
int OWReadROM()
{
	int loop;

	OWTouchReset();
	OWWriteByte(READ_ROM);
	for (loop = 0; loop < 8; loop++)
	{
	printf("Result of Read after ROM = %x\n",OWReadByte());
	}
}


/* ********************************************************************** */
int OWInit()
{
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(WRITE_SP);
	OWWriteByte(SP_00);
	OWWriteByte(ICA);
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(COPY_SCRATCH_PAD);
	OWWriteByte(SP_00);
// must wait for eeprom write
	tickDelay(9000);
	tickDelay(9000);
	tickDelay(9000);
}

/* ********************************************************************** */
int OWReadTemp_Volts_Current()
{
	int temp_lsb, temp_msb, volts_lsb, volts_msb, current_lsb, current_msb;

	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(CONVERT_Temp);
	tickDelay(9000);
	tickDelay(9000);
	tickDelay(9000);
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(CONVERT_Voltage);
	tickDelay(9000);
	tickDelay(9000);
	tickDelay(9000);
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(RECALL_Memory);
tickDelay(9000);
	OWWriteByte(RECALL_PAGE00);
	tickDelay(9000);
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(READ_SCRATCH_PAD);
tickDelay(9000);
	OWWriteByte(READ_PAGE00);
tickDelay(9000);
	status_config = OWReadByte();
printf("OWW STATUS_CONFIG 1st = %4x\n",status_config);
if ( status_config != 0x1)
	{
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(READ_SCRATCH_PAD);
	OWWriteByte(READ_PAGE00);
	status_config = OWReadByte();
printf("OWW STATUS_CONFIG 2nd = %4x\n",status_config);
	}
	temp_lsb = OWReadByte();
	temp_msb = OWReadByte();
	volts_lsb = OWReadByte();
	volts_msb = OWReadByte();
	current_lsb = OWReadByte();
	current_msb = OWReadByte();
	// plus two more byte for completeness
	OWReadByte();
	OWReadByte();
	OWTouchReset();
// printf("OWW STATUS_CONFIG = %4x\n",status_config);
printf("OWW VoltageLSB = %2x\n",volts_msb);
printf("OWW VoltageMSB = %2x\n",volts_lsb);
// printf("OWW AMPSMSB = %2x\n",current_msb);
// printf("OWW AMPSLSB = %2x\n",current_lsb);

	volts_msb  <<= 8 ;
	temp_msb <<= 8 ;
	current_msb <<= 8 ;
	voltage = volts_msb | volts_lsb ;
	float_voltage = voltage * 3 ;
	float_voltage /= 100 ;
      temperature = temp_msb | temp_lsb ;

      // find if temperature sign is positive or negative
	if (temperature > 0x8000)
	{
	resolution = -0.03125 ;
	temperature = ~temperature ;
	temperature = temperature + 1 ;
	temperature = temperature & 0x0000ffff ; 
	}
	else
	resolution = 0.03125 ;

	temperature >>= 3 ; // down shift
	float_temperature = temperature ;
	float_temperature = float_temperature * resolution ;
	current = current_msb | current_lsb ;

// printf("OWW Voltage response = %2.2f\n",float_voltage);
// printf("OWW Temperature response = %2.5f\n",float_temperature);

// these numbers 3 and 572 empirically calculated 
   float_current = current * 3 ;
   float_current = float_current /571 ;
// printf("OWW AVG Current in  = %5.6f mA\n",float_current);

// printf("\n");
}
/* ********************************************************************** */
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
