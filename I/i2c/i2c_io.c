
/* 
A modified version of devmem.c to support I2C i/o
written RR 08/06/05
changed to store results in RAM
@ MCM 10/30/05
 */
/* altered at Rose Bay for PenguinCam board on 9/17/06 */
/* altered at Mona Vale for Patriot Hills board on 8/12/07 */
/* added at Mona Vale for Patriot Hills board on 8/25/07 solar sensor input on chanels 1 and 2*/
/* at RB 9/15/09 changed the fprintf to include solar_2 data as well as solar_1 for the amigos units */
/* added a utility to read data from a voltage calibration file to use in the calculation of ADC voltage */

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
#define FILEOPEN3 "voltage_cal"

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

	float avg_temperature, float_temperature , solar_1, solar_2, volts_cal_factor;
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
	
	FILE  *fp1, *fp2, *fp3;

	/* open files for writing */
          fp1 = fopen("/var/voltage","w");
          if (fp1 < 0)
          {
          perror(FILEOPEN1);
          exit (-1);
          }

	  fp2 = fopen("/var/voltagedata","a");
          if (fp2 < 0)
          {
          perror(FILEOPEN2);
          exit (-1);
          }
	  
     if((fp3 = fopen("/mnt/i2c/voltage_cal","r"))==NULL)
          {
          printf("no voltage cal file\n");
	    volts_cal_factor = 17.836 ; // avg of A1 to A5   
          }
	    else
	    { 	 	
		// get the ADC cal factor for voltage readings

              fscanf (fp3, "%f", &volts_cal_factor);
              fclose (fp3);
              printf ("voltage cal factor is: %2.2f \n",volts_cal_factor);
	    }
	
init_gpio() ;
get_i2c_data() ;
// must do OWInit to flash eeprom first time PCB init'ed
// OWInit() ;
OWReadTemp_Avg() ;
// get_Tilt() ;

time_t now;				/* define 'now'. time_t is probably
					 * a typedef	*/

    time(&now);
    l_time = localtime(&now);
    strftime(string, sizeof string,"%m%d%y %H%M%S", l_time);
    printf("%s \n", string);

printf("Input voltage = %03.3fV\n", avg_voltage );
printf("Input current = %03.3fA\n", avg_current );
printf("PCB temperature = %03.3fC\n", avg_temperature );
printf("Solar_1 = %01.3fV, Solar_2 = %01.3fV\n", solar_1, solar_2);
	
fprintf(fp1,"%s %03.1f %03.3f %03.1f %03.3f %03.3f\n",string,avg_voltage, avg_current,avg_temperature, 
solar_1, solar_2) ;
fprintf(fp2,"%s %03.1f %03.3f %03.1f %03.3f %03.3f\n",string,avg_voltage, avg_current,avg_temperature,
solar_1, solar_2) ;

	fclose(fp1);
	fclose(fp2);
	close(fd);

	// we used to save to flash every minute but now to RAM
	// system("cp /mnt/i2c/voltage /var/voltage");
	// system("cp /mnt/i2c/voltagedata /var/voltagedata");

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
delay(1); //added 9/17/06
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
I2C_high_SCL();          // and then clock
read_result = I2CReport() ; // Reports the status of the acknowledge condition.
delay(1);
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
delay(1); //was 1 delay 9/17/06
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

}
/* ********************************************************************** */
int I2C_high_SCL()     
{
// printf("in I2C_high_SCL\n");

	virt_addr = map_base + (GPSR2 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = SCL_bit ; // make hard logic one
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

}
/* ********************************************************************** */
int I2C_low_SCL()
{
// printf("in I2C_low_SCL\n");

	virt_addr = map_base + (GPCR2 & MAP_MASK) ;
    	*((unsigned long *) virt_addr) = SCL_bit ; // make hard logic zero
}
/* ********************************************************************** */
int get_i2c_data()
{
	int i;
	char count ;
	int return_code;
  	char x_cal, y_cal;
   	float voltage, current, x_voltage, y_voltage ;

	avg_voltage = avg_current = solar_1 = solar_2 =0;

   	// printf("channel = %d\n", channel);

   //// set CS0,1 to 11, convert from 0 - 3
   I2C_start() ;
   // if (return_code)
   // printf("i2c_start returned:%d\n", return_code);
   return_code = I2C_out_byte(0xc8) ; //write command
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
   return_code = I2C_out_byte(0xd0) ; //setup byte command, use 2.048v ref
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);
   return_code = I2C_out_byte(0x07) ; //configuration byte command
   	if (return_code)
   		printf("I2C_out_byte command returned: %d\n", return_code);

   I2C_stop() ;

// loop start
for (count = 0; count < 20; count++)
   {
   I2C_start() ;

   return_code = I2C_out_byte(0xc9) ; // read command
   if (return_code)
   	printf("I2C_out_byte returned:%d\n", return_code);

   delay(2) ;

   return_code = I2C_in_byte_rr() ;
   //if (return_code)
   	// printf("I2C_in_byte_rr_first returned: %d\n", return_code);
   SendAck();
	x_voltage = (float)return_code ;
        ///channel 0 done
	return_code = I2C_in_byte_rr() ;
   //if (return_code)
   	// printf("I2C_in_byte_rr_second returned: %d\n", return_code);
   SendAck();
	y_voltage = (float)return_code ;
        ///channel 1 done
	return_code = I2C_in_byte_rr() ;
   //if (return_code)
   	// printf("I2C_in_byte_rr_third returned: %d\n", return_code);
   SendAck();
	voltage = (float)return_code ;
        ///channel 2 done
	return_code = I2C_in_byte_rr() ;
   //if (return_code)
   	// printf("I2C_in_byte_rr_fourth returned: %d\n", return_code);
          ///channel 3 done  
   SendNAck();
	current = (float)return_code ;

      voltage = ( voltage / 255) ;
      // voltage *= 17.85 ; //changed at mona vale for Wx7 08/12/07 this is 255 for 75k/10k
      // voltage *= 17.96 ; //changed at RB for Amigos1 2/14/09 RR
      // voltage *= 17.50 ; //changed at RB for Amigos2 9/15/09 RR
      // voltage *= 17.87 ; //changed at RB for Amigos3 9/15/09 RR
      // voltage *= 18.20 ; //changed at RB for Amigos4 9/15/09 RR
      // voltage *= 17.63 ; //changed at RB for Amigos5 9/15/09 RR

         voltage *= volts_cal_factor  ; //changed at RB, cal factor read from a file in /mnt/i2c/ 9/15/09 RR
 
     avg_voltage = avg_voltage + voltage ;

      current = (current/255) ;
      avg_current = avg_current + current ;

      x_voltage = (x_voltage/255) ;
      solar_1 	= solar_1 + x_voltage ;
      y_voltage = (y_voltage/255) ;
      solar_2	= solar_2 + y_voltage ;	
	  
   I2C_stop() ;
   
   }

   avg_voltage = avg_voltage / 20 ; // divide cumulated result.
   avg_current = avg_current / 20 ; // divide cumulated result.

// printf("avg_current  = %.4f\n",avg_current); 

if ( avg_current > 0.800 && avg_current < 1.000 ) // 5 Amp
avg_current *= 5.025 ;
if ( avg_current > 0.700 && avg_current < 0.800 ) // 4 Amp
avg_current *= 5.05 ;
if ( avg_current > 0.600 && avg_current < 0.700 ) // 2.5 - 3 Amp
avg_current *= 5.06 ;
if ( avg_current > 0.500 && avg_current < 0.600 ) // 2 - 2.5 Amp
avg_current *= 5.07 ;
if ( avg_current > 0.350 && avg_current < 0.500 ) // 2 Amp
avg_current *= 5.095 ;
if ( avg_current > 0.250 && avg_current < 0.350 ) // 1 Amp
avg_current *= 5.10 ;
if ( avg_current > 0.150 && avg_current < 0.250 ) // 1 Amp
avg_current *= 5.115 ;
if (avg_current > 0.050 && avg_current < 0.150) // < 1 Amp
avg_current *= 5.30 ;
if (avg_current > 0.010 && avg_current < 0.050) // < 1 Amp
avg_current *= 5.40 ;


// 5.03 good for 4.9 Amps
// 5.05 good for 4 Amps
// 5.07 good for 3 Amps
// 5.095 good for 2 Amps
// 5.115 good for 1 Amps

	solar_1 = ( solar_1/20 ) * 2.048  ; 
	solar_2 = ( solar_2/20 ) * 2.048 ;

	// printf("solar_1 = %.4f, solar_2 = %.4f\n",(solar_1 * 2.048),(solar_2 * 2.048)); 
    
	// printf(" solar 1 = %.4f, solar 2 = %.4f \n", solar_1, solar_2) ;
   	// printf("Read_voltage_x = %.4f\n",x_voltage);
  	// printf("Read_voltage_y = %.4f\n",y_voltage);
	// printf("Read_voltage = %.4f\n",avg_voltage);
	// printf("Read_current = %.4f\n",avg_current);

   //////////// the end
   // return avg_voltage;
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
	int temp_lsb, temp_msb, temperature ;
	int status_config ;
        float resolution;

	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(CONVERT_Temp);
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
// printf("OWW STATUS_CONFIG 1st = %4x\n",status_config);
if ( status_config != 0x1)
	{
	OWTouchReset();
	OWWriteByte(SKIP_ROM);
	OWWriteByte(READ_SCRATCH_PAD);
	OWWriteByte(READ_PAGE00);
	status_config = OWReadByte();
// printf("OWW STATUS_CONFIG 2nd = %4x\n",status_config);
	}
	temp_lsb = OWReadByte();
	temp_msb = OWReadByte();
	OWTouchReset();
// printf("OWW STATUS_CONFIG = %4x\n",status_config);
	temp_msb <<= 8 ;
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
// printf("OWW Temperature response = %2.5f\n",float_temperature);

}

/* ********************************************************************** */
int OWReadTemp_Avg()
{
average_count = 10;
avg_temperature = 0 ;
int avgloop ;

for (avgloop = 0; avgloop < average_count ; avgloop++)
	{
	OWReadTemp_Volts_Current();
	avg_temperature = avg_temperature + float_temperature ;
	}

avg_temperature = avg_temperature / average_count ;
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
/* ********************************************************************** */
int delay(int dly)
{

// printf("in delay\n");

int t;
t = dly;
for (t=0;t<10000;t++);
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

