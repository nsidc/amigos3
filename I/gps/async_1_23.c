/********************************************************************
** @source ASYNC MESSAGE LOGGER for the Garmin GPS12 or XL
**
** @author Copyright (C) 2000,2001 Antonio Tabernero
** @version 1.22
** @modified Jun 28 2000 Antonio Tabernero. First version
** @last modified Apr 10 2001  Antonio Tabernero. 
** @last modified Apr 21 2001  Antonio Tabernero. 
** @last modified Jun 25 2001  Antonio Tabernero. 
** @last modified Sep  3 2001  Antonio Tabernero
** @last modified Mar 23 2002  Antonio Tabernero
** @@
**
** This library is free software; you can redistribute it and/or
** modify it under the terms of the GNU Library General Public
** License as published by the Free Software Foundation; either
** version 2 of the License, or (at your option) any later version.
**
** This library is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
** Library General Public License for more details.
**
** You should have received a copy of the GNU Library General Public
** License along with this library; if not, write to the
** Free Software Foundation, Inc., 59 Temple Place - Suite 330,
** Boston, MA  02111-1307, USA.
********************************************************************/ 

/****************************************************************
1.23   * Option -all to log the serial port stream directly to a file
       * Option -stdout to redirect the output to the standard output 

1.21   * Some minor bugs corrected (thanks to Michal Hobot) and some 
         parameters modified to improve comms with some Garmin models
		 (thanks to Jim Harris).

1.20   * Get what I believe is Doppler shift info using the +doppler flag.

1.15   * Uses Garmin protocol to log position and UTC time for those 
         units (i.e. Garmin 175) without a 0x33 record.
       * Tried to improve IO comms (dont know if it's any better, though) 
       * Dumps IO comms to file "trace.txt" if TRACE_IO defined.
  
1.10   * Common code for both gcc (Linux) and VisualC++(W95)
       * Fix the DLE,ETX bug
       * Do not save packets with bad checksums
       * Relax the fix condition on 0x33 records (for eMap, etrex)

1.00   First version
*****************************************************************/

//Comment this line for compilation with VisualC
#define  LINUX   


#define VERSION 1.21

//Uncomment this only for serial IO debugging  purposes 
#define TRACE_IO  



#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <string.h>

#include <time.h>
#include <sys/types.h>
#include <sys/timeb.h>

#ifdef LINUX
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>        
#else
#include <windows.h>
#include <winbase.h>  
#endif



#ifdef TRACE_IO
#define TRACE_FILE "trace.txt"
  FILE* TRACE;
#endif



/////////////////////////////////////////////////////////////////////
// Possible commands
/////////////////////////////////////////////////////////////////////
#define CHECK 1
#define IDENT 2
#define ASYNC 3
#define REQST 4
#define RINEX 5
#define DOPPLER 6 
#define TEST 11  
#define LOG_ALL 12

/////////////////////////////////////////////////////////////////////
// Default Arguments
/////////////////////////////////////////////////////////////////////
#define DEF_COMMAND  IDENT    // Get product ID                        
#define DEF_FLAG     0xffff     // All events
#define DEF_FLAG_REQUEST 0x0001     // Default Request
#define DEF_LOG_TIME 30         // 30 sec 
#define DEF_VERBOSE_LEVEL 1     // Verbosity level

#ifdef LINUX
#define DEF_PORT     "/dev/ttyS0"     // use first port "COM1"
#else
#define DEF_PORT     "com1"     // use COM1    
#define M_PI 3.141592653589793
#endif


/////////////////////////////////////////////////////////////////////


#define ID_PACKET   inbuffer[0]    // ID Position in Packet
#define L_PACKET    inbuffer[1]    // Length Position in Packet
#define DATA_PACKET (inbuffer+2)   // Data Position in Packet
#define INI_PACKET  inbuffer


#define MAXBUF 512

#define EOD 0x0C    // End of Data (in request commands)

#define DLE 0x10
#define ETX 0x03

#define ACK 0x06
#define NAK 0x15


#define DAT_ST 0
#define DLE_ST 1
#define ETX_ST 2 


#define MAX_FAILED 50


/////////////////////////////////////////////////////////////////////

// Error codes

#define E_ABRIR   0
#define E_SETUP   1
#define E_GETCOMM 2
#define E_SETCOMM 3
#define E_GETTIME 4
#define E_SETTIME 5
#define E_PURGE   6
#define E_CERRAR  7 

#define E_READ 8
#define E_TIMEOUT 9
#define E_EXPECTED_ACK 10
#define E_EXPECTED_PACKET 11

#define E_WRITE 16
#define E_WRITE_SHORT 17

#define E_ORDEN 31


//////////////////////////////////////////////////////////////////////
//Types

#ifdef LINUX
typedef unsigned char BOOLEAN;
#else
#endif

typedef unsigned char BYTE;
typedef unsigned long ULONG;
typedef long int LONG;
typedef unsigned int UINT;
typedef struct {double lat; double lon;} D_POS; 




/////////////////////////////////////////////////////////////////////7
// Global variables

ULONG CHARS_READ;

BOOLEAN CHKSUM=0;
BOOLEAN ACK_PACKETS=1;

int rx_state = DAT_ST;

BYTE buffer[MAXBUF];
BYTE inbuffer[MAXBUF];

char PORT[32];
ULONG *p_error_code;
ULONG READ_TIMEOUT=100;
BYTE verbose;

BOOLEAN STDOUT=0;

#ifdef LINUX
int  pcom;
static struct termios gps_ttysave;        
#else
HANDLE  pcom;  
#endif


#ifdef LINUX
///////////////   FUNCTION DECLARATIONS  //////////////////////////

////////////////////////////////////////////////////////////////////
/// (Basic IO Comm for Linux (Jeeps Library)
////////////////////////////////////////////////////////////////////
/********************************************************************
** @source JEEPS serial port low level functions
**
** @author Copyright (C) 1999 Alan Bleasby
** @version 1.0
** @modified Dec 28 1999 Alan Bleasby. First version
** @modified Jun 28 2000 Antonio Tabernero.
** @@
**
** This library is free software; you can redistribute it and/or
** modify it under the terms of the GNU Library General Public
** License as published by the Free Software Foundation; either
** version 2 of the License, or (at your option) any later version.
**
** This library is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
** Library General Public License for more details.   
*********************************************************************/               
///////////////////////////////////////////////////////////////////////

int  GPS_Serial_Chars_Ready(int fd);
int  GPS_Serial_Close(int fd, const char *port);
int  GPS_Serial_Open(int *fd, const char *port);
int  GPS_Serial_Restoretty(const char *port);
int  GPS_Serial_Savetty(const char *port);
int  GPS_Serial_On(const char *port, int *fd);
int  GPS_Serial_Off(const char *port, int fd);
int  GPS_Serial_Wait(int fd);
int  GPS_Serial_Flush(int fd);
/////////////////////////////////////////////////////////////////////
/////////////////  END JEEPS LIBRARY ///////////////////////////////
#endif

/////////// Serial Port Functions
BOOLEAN open_port(char *ComPort);
BOOLEAN close_port();   

/////////// Serial Port Functions
void set_error(BYTE b);

/////////// Serial Port Read Functions
UINT read_data(BOOLEAN responde);
UINT read_packet();
BOOLEAN read_char(BYTE *bptr);
UINT strip_packet(UINT n, BYTE *ack);
UINT send_ack(BYTE id,BYTE ok);
void show_in(UINT n);

/////////// Serial Port Write Functions
UINT build_packet(BYTE *data);
UINT read_ack(BYTE id);
UINT send_packet(BYTE *data);
void show_out(UINT n);

///////// Auxiliar functions
UINT get_uint(BYTE* ptr);
ULONG get_long(BYTE* ptr);

/////////  GPS related functions
void ident();
BOOLEAN async(int flag_async);
void log_packets_0x33(FILE *fich);
void log_packets_async(int flag,double T_LOG,FILE *fich);
ULONG log_packets_request(UINT flag_request, FILE *fich);



///////////////   FUNCTION DEFINITIONS  //////////////////////////



#ifdef LINUX

////////////////////////////////////////////////////////7

////////////////////////////////////////////////////////////////////
/// Jeeps Library Low Level IO Comm function definitions
////////////////////////////////////////////////////////////////////
/********************************************************************
** @source JEEPS serial port low level functions
**
** @author Copyright (C) 1999 Alan Bleasby
** @version 1.0
** @modified Dec 28 1999 Alan Bleasby. First version
*********************************************************************/

int GPS_Serial_Savetty(const char *port)
{
    int fd;
 
    if((fd = open(port, O_RDWR|O_NDELAY))==-1)
    { set_error(E_ABRIR); return 0; }
 
    if(tcgetattr(fd,&gps_ttysave)==-1)
    { set_error(E_GETCOMM); return 0; }
 
    if(!GPS_Serial_Close(fd,port)) { return 0; }
 
    return 1;
}                       

int GPS_Serial_Open(int *fd, const char *port)
{
    struct termios tty;
 
    if((*fd = open(port, O_RDWR | O_NDELAY))==-1)
    { set_error(E_ABRIR); return 0; }
 
    if(tcgetattr(*fd,&tty)==-1)
    { set_error(E_GETCOMM); return 0; }
 
    tty.c_cflag = (CBAUD & B4800);
    tty.c_cflag |= (CSIZE & CS8);
    tty.c_cflag |= CREAD;
 
    tty.c_lflag &= 0x00000000;
    tty.c_iflag = tty.c_oflag = tty.c_lflag;
    tty.c_oflag |= ONLRET;
                                                 
    if(tcsetattr(*fd,TCSANOW,&tty)==-1)
    { set_error(E_SETCOMM); return 0; }

printf("in GPS_Serial_Open\n");
     
    return 1;
}                

int GPS_Serial_On(const char *port, int *fd)
{
    if(!GPS_Serial_Savetty(port))  return 0; 
    if(!GPS_Serial_Open(fd,port))  return 0; 

    return 1;
}                             

int GPS_Serial_Restoretty(const char *port)
{
    int fd;
 
    if((fd = open(port, O_RDWR|O_NDELAY))==-1)
    { set_error(E_ABRIR); return 0; }
 
    if(tcsetattr(fd, TCSAFLUSH, &gps_ttysave)==-1)
    { set_error(E_SETCOMM); return 0; }
 
    return 1;
}
                               

int GPS_Serial_Close(int fd, const char *port)
{
    if(close(fd)==-1) { set_error(E_CERRAR); return 0; }
    return 1;
}                      

int GPS_Serial_Off(const char *port, int fd)
{
    if(!GPS_Serial_Close(fd,port))  return 0;
 
    if(!GPS_Serial_Restoretty(port)) return 0;
 
    return 1;
}                     

int GPS_Serial_Chars_Ready(int fd)
{
    fd_set rec;
    struct timeval t;
 
    FD_ZERO(&rec);
    FD_SET(fd,&rec);
 
    t.tv_sec  = 0;
    t.tv_usec = 0;
 
    (void) select(fd+1,&rec,NULL,NULL,&t);
    if(FD_ISSET(fd,&rec))
        return 1;

printf("in GPS_Serial_Chars_Ready\n");
 
    return 0;
}
                   
int purge_comm(int fd)
{
 BYTE x;
 int res,i;

#ifdef TRACE_IO
 fprintf(TRACE,"Purging comm port : ");
#endif

 i=0;
 while (GPS_Serial_Chars_Ready(fd)) 
  { 
   res=read(fd,&x,1); 
   i++; 
#ifdef TRACE_IO
  fprintf(TRACE,"%02x ",x);
#endif         
  }     

#ifdef TRACE_IO
 fprintf(TRACE,":: %d chars purged\n",i);
 fflush(TRACE);
#endif

 return i; 
}
          
//////////////END JEEPS FUNCTIONS //////////////////////
//////////////////////////////////////////////////////////
#endif

/////////// Serial Port Open & Close Functions
////////////////////////////////////////////////////////////

BOOLEAN open_port(char *ComPort)
{
#ifdef LINUX
/////////////////////////////////////////// Linux code
  BOOLEAN res;
  res=(BOOLEAN) GPS_Serial_On(ComPort, &pcom);
  return(res);
#else
/////////////////////////////////////////// VC++ code
   DCB      m_dcb;
 COMMTIMEOUTS m_CommTimeouts;
 
 pcom = CreateFile(ComPort, GENERIC_READ | GENERIC_WRITE,
                0, // exclusive access
                NULL, // no security
                OPEN_EXISTING,
                0, // no overlapped I/O
                NULL); // null template
 
 if (pcom==INVALID_HANDLE_VALUE)
  {
#ifdef TRACE_IO
   fprintf(TRACE,"Can't open port %s\n",ComPort); fflush(TRACE);
#endif
   set_error(E_ABRIR);  return 0;
  }
  else
  {
#ifdef TRACE_IO
   fprintf(TRACE,"Port  %s Open\n",ComPort); fflush(TRACE);
#endif
  }
 
// Input/Output buffer size
 if( SetupComm(pcom, MAXBUF, MAXBUF)==0)
  { close_port(); set_error(E_SETUP); return 0;  }
                                                                      
// Port settings are specified in a Data Communication Block (DCB).
// The easiest way to initialize a DCB is to call GetCommState
// to fill the default values, override the values that you
// wannna change and then call SetCommState to set the values.
 
 if (GetCommState(pcom, &m_dcb)==0)
  { close_port(); set_error(E_GETCOMM);  return 0;}
 
 m_dcb.BaudRate = 9600;
 m_dcb.ByteSize = 8;
 m_dcb.Parity = NOPARITY;
 m_dcb.StopBits = ONESTOPBIT;
 m_dcb.fAbortOnError = TRUE;
 
 
 if(SetCommState(pcom, &m_dcb)==0)
  { close_port(); set_error(E_SETCOMM);  return 0;}
 
// Optional Communication timeouts can be set similarly:
 
 if(GetCommTimeouts (pcom, &m_CommTimeouts)==0)
  {
   close_port(); set_error(E_GETTIME);  return 0;
  }
 
 
m_CommTimeouts.ReadIntervalTimeout = 1; //50;
m_CommTimeouts.ReadTotalTimeoutConstant = 0; //50;
m_CommTimeouts.ReadTotalTimeoutMultiplier = 0; //10;
m_CommTimeouts.WriteTotalTimeoutConstant = 50;
m_CommTimeouts.WriteTotalTimeoutMultiplier = 10;
 
 if (SetCommTimeouts (pcom, &m_CommTimeouts)==0)
  {
   close_port(); set_error(E_SETTIME);  return 0;
  }
 
 
// Purging comm port at start
 
 if (PurgeComm(pcom,PURGE_TXCLEAR | PURGE_RXCLEAR)==0)
  {
   close_port(); set_error(E_PURGE);  return 0;
  }
 
 return 1;                                           

#endif

}


BOOLEAN close_port()
{
#ifdef LINUX
/////////////////////////////////////////// Linux code
  BOOLEAN res;
  res=(BOOLEAN)GPS_Serial_Off(PORT,pcom);
  return res;     
#else
/////////////////////////////////////////// VC++ code 
  if (CloseHandle(pcom)==0) { set_error(E_CERRAR);  return 0; }
  #ifdef TRACE_IO
    fprintf(TRACE,"Port closed\n---------------------------------\n"); fflush(TRACE);
  #endif
  return 1;      
#endif
}


/////////////////////////////////////////////////////////////
// Serial Port IO Debugging Functions 

void show_in(UINT n)
{
#ifdef TRACE_IO
	UINT k;
	fprintf(TRACE,"IN : ");
	for(k=0;k<n;k++) fprintf(TRACE,"%02X ",inbuffer[k]);
	fprintf(TRACE,"\n");//	getchar();
	fflush(TRACE);
#endif 
}

void show_out(UINT n)
{
#ifdef TRACE_IO
	UINT k;
	fprintf(TRACE,"OUT: ");
	for(k=0;k<n;k++) fprintf(TRACE,"%02X ",buffer[k]);
    fprintf(TRACE,"\n");//	getchar();
    fflush(TRACE);
#endif 
}


/////////////////////////////////////////////////////////////////////////
// void PAUSA(msec) Wait for msec milliseconds 
/////////////////////////////////////////////////////////////////////////
void pausa(double msec)    // Pausa de msec msec
{
 double CPMS=CLOCKS_PER_SEC/1000.0;
 clock_t start=clock();

 while ( (clock()-start)/CPMS < msec)
  {
  } 
}

/////////////////////////////////////////////////////////////////////////
// Eliminates start/end and repeated DLE bytes and check CHECKSUM
/////////////////////////////////////////////////////////////////////////
UINT strip_packet(UINT n, BYTE *ack)
{
 UINT k,cont,maxn;
 BYTE x,chk,chk_rec,id;
 
 chk_rec=inbuffer[n-3];
 maxn=n-3; if (chk_rec==DLE) maxn--;

 chk=0;
 for(k=1,cont=0;k<maxn;k++)
 {
  x=inbuffer[k]; chk+=x;
  inbuffer[cont++]=x;
  if (x==DLE) k++;
 }
 chk=-chk;

 id=inbuffer[0];

#ifdef TRACE_IO
 fprintf(TRACE,"ID de packet %02X\n",id); fflush(TRACE);
#endif

 *ack = (chk == chk_rec);  

 return cont;
}

/////////////////////////////////////////////////////////////////////////
// WAIT UNTIL A CHAR (*x) IS READ FROM SERIAL PORT OR A TIMEOUT OCCURS
// RETURN 0 when TIMEOUT, 1 if OK 
/////////////////////////////////////////////////////////////////////////
BOOLEAN read_char(BYTE *x)
{
#ifdef LINUX
/////////////////////////////////////////// Linux code

  double CPMS=CLOCKS_PER_SEC/1000.0;
  clock_t start=clock();
  int res;

printf("I get to here before routine?\n");
  
  do
   {
    res=GPS_Serial_Chars_Ready(pcom);
    if ( (clock()-start)/CPMS> READ_TIMEOUT) 
     {
       set_error(E_TIMEOUT); //close_port();
printf("I get to here @ E-TIMEOUT routine?\n"); 
	   return 0;  
#ifdef TRACE_IO
       fprintf(TRACE,"TIMEOUT esperando caracter\n"); fflush(TRACE);
#endif           
     }
   }
  while (res==0);

printf("after do while routine?\n");
 
   res=read(pcom, x, 1); 
#ifdef TRACE_IO	   
       printf("READ Operation %d\n",res);
#endif
   if (res==-1) {set_error(E_READ); close_port(); return 0;} 

  CHARS_READ++;
  return res;

printf("did I get to here?\n");

#else
/////////////////////////////////////////// VC++ code 

  //UINT nb;
  ULONG nb;
  double CPMS=CLOCKS_PER_SEC/1000.0;
  clock_t start=clock();
  BOOLEAN res;
 
  do
    {
     if ( (clock()-start)/CPMS> READ_TIMEOUT)
      {
       set_error(E_TIMEOUT); //close_port(); 
       return 0;
#ifdef TRACE_IO
       fprintf(TRACE,"TIMEOUT waiting for a char\n"); fflush(TRACE);
#endif
      }
     res=ReadFile(pcom, x, 1, &nb, NULL);
     if (res==0) {set_error(E_READ); close_port(); return 0;}
    }
  while (nb==0);
 
  CHARS_READ++;
  return (BOOLEAN)nb;                     

#endif
}


/////////////////////////////////////////////////////////////////////////
// READ SERIAL PORT UNTIL THE END OF PACKET is DETECTED
// THE PACKET (ALREADY STRIPPED) IS FOUND in INBUFFER[]
// ERRORS: READ ERROR in PORT
//         PACKET LONGER THAN MAXBUF
// RETURN number of bytes in packet (OK) or 0 (ERROR)
/////////////////////////////////////////////////////////////////////////
UINT read_packet()
{
 UINT buf_ptr;
 BYTE c;

 buf_ptr=0;
  
 while(1) 
   {
    if (read_char(&c)==0) return 0;

printf("read data = %s\n",inbuffer);

    switch (rx_state)
     {
      case DAT_ST: if (c==DLE) rx_state=DLE_ST; else inbuffer[buf_ptr++]=c;
                   break;
      case DLE_ST: if (c==ETX)
                    {
                     rx_state=ETX_ST;
                     return buf_ptr;
                    }
                   else
                    {
                     inbuffer[buf_ptr++]=c;
                     rx_state=DAT_ST;
                    }
                   break;
      case ETX_ST: if (c==DLE) rx_state=DLE_ST;
                   break;
      default: if (buf_ptr==MAXBUF) return 0;
     }                                      
   }
}


void check_packet(UINT n)
 {
  UINT k;
  BYTE chksum=0;

  for (k=0;k<n;k++) chksum+=inbuffer[k];

  CHKSUM=(BOOLEAN)(chksum==0);

#ifdef TRACE_IO
  if (CHKSUM) fprintf(TRACE,"CHKSUM OK\n"); else fprintf(TRACE,"BAD CHKSUM\n");
  fflush(TRACE);
#endif
 }
                                                       

/////////////////////////////////////////////////////////////////////////
// TRY TO READ AN EXPECTED PACKET FROM SERIAL PORT.
// IF answer==1, SEND AN ACK/NACK packet. 
// IN case of error, it tries to read it again until it is ACKed.
// RETURN 0 (if error) or the number of bytes in the packet received.
// When done, the stripped packet is place in INBUFFER[]
/////////////////////////////////////////////////////////////////////////
UINT read_data(BOOLEAN answer)
{
 UINT nb;
 BYTE id;
 
 nb=read_packet(); if (nb==0) {set_error(E_EXPECTED_PACKET); return 0;}
 show_in(nb);

 check_packet(nb);
 
 if (answer)
 {
  id=inbuffer[0];
  send_ack(id,CHKSUM);
  if (CHKSUM==0) nb=read_data(1);  
 }

 return nb;
}



/////////////////////////////////////////////////////////////////////////
// Prepares the data contained in data[] as a proper Garmin IO packet 
// REturn the length of the resulting packet
/////////////////////////////////////////////////////////////////////////
UINT build_packet(BYTE *data)
{
 BYTE chk;
 UINT k,cont,L;

 L=(UINT)data[1];
 chk=0; cont=0;

 // Inicio
 buffer[cont++]=DLE;
 
 // Data
 for(k=0;k<L+2;k++)
 {
  chk=chk+data[k];
  buffer[cont++]=data[k]; 
  if (data[k]==DLE) buffer[cont++]=DLE;
 }
 
 // Checksum
 chk=-chk;
 buffer[cont++]=chk; if (chk==DLE) buffer[cont++]=DLE;
 
 // End
 buffer[cont++]=DLE;
 buffer[cont++]=ETX;
 
 return cont;
}	 


/////////////////////////////////////////////////////////////////////////
// SEND an ACK (ok=1) or NACK (ok=0) to a received packet of identity id
// Returns 0 (in error) or  number of bytes written to the comm port
/////////////////////////////////////////////////////////////////////////
UINT send_ack(BYTE id,BYTE ok)
{
 UINT nbytes,r;
#ifdef LINUX 
 int n; 
#else 
 ULONG n; 
#endif
 BYTE data[4];

 data[0]= (ok)? ACK:NAK; 
 data[1]=0x02;
 data[2]=id; data[3]=0x00;

 #ifdef TRACE_IO
   if (ok) fprintf(TRACE,"Received correct packet ID %02X -> ACK sent back ",id);
   else fprintf(TRACE,"Received bad packet ID %02X -> NAK sent back ",id);
   fflush(TRACE);
 #endif
 
 nbytes=build_packet(data);

#ifdef LINUX
  n = write(pcom,buffer,nbytes);
  if (n==-1) {set_error(E_WRITE);  close_port(); return 0;}
#else
  r = WriteFile(pcom,buffer,nbytes,&n,NULL);
  if (r==0) {set_error(E_WRITE); close_port(); return 0;}
#endif

 if ((UINT)n<nbytes) {set_error(E_WRITE_SHORT); close_port(); return 0;}
 show_out((UINT)n);


 //if (r==0) { printf("Error en puerto\n"); return 0;}
 //if (r<nbytes) { printf("Prob escribiendo Puerto\n"); return 0;}

 return n;
}


/////////////////////////////////////////////////////////////////////////
// Wait WAIT_FOR_ACK msec listening for an ACK/NCK packet
/////////////////////////////////////////////////////////////////////////
UINT read_ack(BYTE id)
{
 UINT BytesRead;
 BYTE ack;
 double WAIT_FOR_ACK=50;

 pausa(WAIT_FOR_ACK);
 BytesRead=read_packet(); 
 if (BytesRead==0) {set_error(E_EXPECTED_ACK);  return 0;}
 check_packet(BytesRead);
 show_in(BytesRead);
 
 ack=inbuffer[0];
 
#ifdef TRACE_IO
 // if (ack==ACK) printf("ID %02X ACK  ",inbuffer[2]); 
 //if (ack==NAK) printf("ID %02x NAK  ",inbuffer[2]); 
 //fflush(TRACE);
#endif

 return ack;
}



/////////////////////////////////////////////////////////////////////////
// Receives a data packet, wrapps it according to the protocol, and 
// checksums, etc, sends it, and wait for ACK. If not ACKed, it is sent again.
// Returns 0 (if error) or numberofbytes written to comm port .
/////////////////////////////////////////////////////////////////////////
UINT send_packet(BYTE *data)
{
   UINT nbytes;
   int r;
   BYTE id;
   ULONG BytesWritten; //UINT BytesWritten;


   id=data[0];

   nbytes=build_packet(data);

#ifdef LINUX
/////////////////////////////////////////// Linux code
   r = write(pcom,buffer,nbytes); 
   if (r==-1) {set_error(E_WRITE); close_port(); return 0;}
   if (r<nbytes) 
    {
     set_error(E_WRITE_SHORT); close_port(); return 0;
    }
   show_out(r);

   if (ACK_PACKETS==0) {ACK_PACKETS=1; return r;}
   
   r=read_ack(id);
   if (r==0) return(0);
   else
    {
     if (r==NAK) 
	  {
#ifdef TRACE_IO
	   fprintf(TRACE,"Packet ID %02X  NAK by GPS. Sending it again\n",id);
	   fflush(TRACE);
#endif
      r = write(pcom,buffer,nbytes);
      if (r==-1) {set_error(E_WRITE); close_port(); return 0;}
      if (r<nbytes) 
       {
        set_error(E_WRITE_SHORT); close_port();  return 0;
       }
      show_out(r);
     }
    else
     {
#ifdef TRACE_IO	   
	   fprintf(TRACE,"Packet ID %02X ACK by GPS\n",id); fflush(TRACE);
#endif
     }   
     return r;
    }
   }

#else
/////////////////////////////////////////// VC++ code 

   r = WriteFile(pcom,buffer,nbytes,&BytesWritten,NULL);
   if (r==0) {set_error(E_WRITE); close_port(); return 0;}
   if (BytesWritten<nbytes) {set_error(E_WRITE_SHORT); close_port(); return 0;}   show_out(BytesWritten);
 
   if (ACK_PACKETS==0) {ACK_PACKETS=1; return r;}

   r=read_ack(id);
   if (r==0) return(0);
   else
    {
     if (r==NAK)
          {
#ifdef TRACE_IO
      fprintf(TRACE,"Packet ID %02X  NAK en destino. Mandamos de nuevo\n",id);
      fflush(TRACE);
#endif
      r = WriteFile(pcom,buffer,nbytes,&BytesWritten,NULL);
      if (r==0) {set_error(E_WRITE); close_port(); return 0;}
      if (BytesWritten<nbytes) {set_error(E_WRITE_SHORT); close_port(); return
0;}
      show_out((UINT)BytesWritten);
     }
    else
     {
#ifdef TRACE_IO
           fprintf(TRACE,"Packet ID %02X ACK en destino\n",id);
		   fflush(TRACE);
#endif
     }
     return BytesWritten;
    }
}                                    
#endif



//////////////////////////////////////////////////////////////
// SEt the error code so that we can know what went astray.
//////////////////////////////////////////////////////////////
void set_error(BYTE n)
{
  *p_error_code |= ((1L)<<n);
#ifdef TRACE_IO
  fprintf(TRACE,"Error# %2d -> Error Code %ld\n",n,*p_error_code);
  fflush(TRACE);
#endif
  return;
}



///////////////////////////////////////////////////////////////////
//// Get uint or ulong in a byte string
/////////////////////////////////////////
UINT get_uint(BYTE* ptr)
  {
   UINT x;

   x= (UINT)(*ptr++);
   x+=256*(UINT)(*ptr);
 
   return x;
  }

ULONG get_long(BYTE* ptr)
  {
   ULONG x;
   
   x=(UINT)(*ptr++);
   x+=(UINT)256*(UINT)(*ptr++);
   x+=(UINT)65536*(UINT)(*ptr++);
   x+=(UINT)16777216*(UINT)(*ptr++);

   return x;
  }


/////////////////////////////////////////////////////////////////////////////
////   GPS related functions
//////////////

////////////////////////////////////////////
//Displays Product ID, soft version, etc
/////////////////

void check_port()
{

 if (open_port(PORT)) 
  {
   printf("Opening port %s\n",PORT);
   if (close_port()) printf("Closing port %s\n",PORT);
  }    

}

void ident()
{
 UINT prod,ver;
 BYTE *bptr=DATA_PACKET;

 BYTE PROD_ID[2] = {0xFE, 0x00};   // Command

 if (open_port(PORT)==0) return;
 if (send_packet(PROD_ID)==0) return;
 if (read_data(1)==0) return;
 if (close_port()==0) return;  
 
 prod=get_uint(bptr); bptr+=2; 
 ver=get_uint(bptr); bptr+=2; 
 printf("Product ID: %d (\"%s\"). Firmware %4.2f\n",prod,(char*)bptr,(float)ver/100.0); 

 return;
}

int get_pos(int p)
{
 double lat,lon;
 BYTE SEND_POS[4]  = {0x0A, 0x02, 0x02, 0x00};     

 if (open_port(PORT)==0) return 0;
 if (send_packet(SEND_POS)==0) return 0;
 if (read_data(1)==0) return 0;

 if(p && verbose)
  { 
   memcpy(&lat,DATA_PACKET,sizeof(double));    lat*=(180/M_PI);
   memcpy(&lon,DATA_PACKET+8,sizeof(double));  lon*=(180/M_PI);
   printf("Position  : Lat %.4f  Long %.4f\n",lat,lon);
  }
  
 close_port();
 return 1;
}                                

double julday (int year,int month,int day, int hour, int min, double sec)
{
 double jd;

 if (month <= 2) {year-=1; month+=12;}
 // jd = floor(365.25*year)+floor(30.6001*(month+1))+day+(hour+(min+sec/60.0)/60.0)/24+1720981.5;    
 jd = (365.25*year)+(30.6001*(month+1))+day+(hour+(min+sec/60.0)/60.0)/24+1720981.5;     
     
 
return jd;
}

double gps_time(double julday, int *week)
{
 double tow,days_gps;
 int wn;
 //int weekday;

 //weekday=floor(julday+0.5)%7  + 1 ;  // 0 Sunday, 1 Monday, ...
 
 days_gps=(julday-2444244.5);
 //wn = (int)floor(days_gps/7);
 wn = (int)(days_gps/7);

 tow = (days_gps- wn*7)*86400;  

 tow=tow+13;  // Correct at least for the 13 leap seconds as of writting this
 if (tow>=604800) { tow-=604800; wn++;} 

 *week=wn;

 return tow;
}

int get_date(int p)
{
  typedef struct {BYTE month; BYTE day; UINT year; UINT hour; BYTE min; BYTE sec;} UTC;
  UTC utc;
  BYTE SEND_TIME[4] = {0x0A, 0x02, 0x05, 0x00};  
  double jd,tow;
  int week;
 
  if (open_port(PORT)==0) return 0;
  if (send_packet(SEND_TIME)==0) return 0;
  if (read_data(1)==0) return 0;

  if(p && verbose)
   { 
    utc.month=inbuffer[2]; 
    utc.day=inbuffer[3];
    utc.year=*((short int*)(inbuffer+4));
    utc.hour=*((short int*)(inbuffer+6));
    utc.min=inbuffer[8]; 
    utc.sec=inbuffer[9];

    jd=julday((int)utc.year,(int)utc.month,(int)utc.day,(int)utc.hour,(int)utc.min,(double)utc.sec);
    tow=gps_time(jd,&week);
 
    printf("Civil Date: ");
    printf("%02u/%02u/%4d ",utc.day,utc.month,utc.year);
    printf("%02d:%02d:%02d\n",utc.hour,utc.min,utc.sec);
    printf("GPS Time  : ");
    printf("GPS Week %4d ToW %6.0f sec. Garmin Weekdays %d\n",week,tow,(week-521)*7);
   }

  close_port();
  return 1;
}
                                        



BOOLEAN async(int flag_async)
{
 BYTE orden[4]={0x1C,0x02,0x00,0x00};
  
 orden[2]=(BYTE)(flag_async%256);  
 orden[3]=(BYTE)(flag_async/256);


 if (flag_async)   //Enabling async events with mask FLAG_ASYNC
   {
    if (open_port(PORT)==0) return 0;
    if (send_packet(orden)==0) return 0;
    if (read_data(0)==0) return 0 ; 
    if (read_data(0)==0) return 0 ;
   }
 else             // Disabling async events
   {
    ACK_PACKETS=0;
    if (send_packet(orden)==0) return 0;
    pausa(600);
#ifdef LINUX
    purge_comm(pcom); 
#else
    if (PurgeComm(pcom,PURGE_TXCLEAR | PURGE_RXCLEAR)==0) return 0;
#endif
    if (close_port()==0) return 0;
   }

 return 1; 
}


int clear_line()
{
 BYTE disable[4]={0x1c, 0x02, 0x00, 0x00};  

#ifdef TRACE_IO
 fprintf(TRACE,"Clearing line\n"); fflush(TRACE);
#endif

 if (open_port(PORT)==0) return 0;

 ACK_PACKETS=0; if (send_packet(disable)==0) return 0;

 pausa(600);
#ifdef LINUX
 purge_comm(pcom); 
#else
 if (PurgeComm(pcom,PURGE_TXCLEAR | PURGE_RXCLEAR)==0) return 0;
#endif

 if (close_port()==0) return 0;

 return 1;
}

void write_packet(FILE *dest)
 { 
  fwrite(INI_PACKET,1,L_PACKET+2,dest);
  fflush(dest); 
 }

void log_packets_0x33(FILE *f_bin)
{
 clock_t start=clock();
 double dt,MAX_WAIT;
 UINT n,fix;
 ULONG rec,ok;
 
 rec=ok=0;
 
 MAX_WAIT=10;                    // Wait 30 seconds for a valid 3D 0x33

 if (verbose)
  {
   printf("-----------------------------------------------------------------\n");
   printf("Waiting for a 3D fix  (%.0f secs at most)\n",MAX_WAIT);
  }
 start=clock();
 if (async(0xffff)==0) return;   // Enable Async messages
 
 READ_TIMEOUT=5000;
 do
  {
   n=read_data(0);
   dt=((double)clock()-start)/CLOCKS_PER_SEC;
   if (n && CHKSUM && (ID_PACKET==0x33) )
     {
      rec++;
      fix=get_uint(DATA_PACKET+16);    //Get type of fix
      if (fix>=3)  { write_packet(f_bin); ok++; }

      //if (fix>=3)  { fwrite(INI_PACKET,1,L_PACKET+2,f_bin); fflush(f_bin); ok++; }
      if (verbose)
       {
        printf("%02.0f secs: %3d 0x33 packets received. %d with a 3D fix%c",dt,rec,ok,13);
       }
     }
  }
 while ((dt<MAX_WAIT) && (ok<5) );
 READ_TIMEOUT=100;           

 async(0);   // Stop Async messages

 if (verbose)
  {
   printf("                                                             %c",13);   
   printf("%02.0f secs: %2d packets with 0x33 ID received. %d with a 3D fix\n",dt,rec,ok);  
  }

 
 if (dt>=MAX_WAIT)
  {
   printf("-----------------------------------------------------------------\n");
   printf("%.0f seconds waiting for 0x33 records with a 3D fix\n",MAX_WAIT);
   printf("Does your GPS screen show a 3D fix?\n");
   printf("You probably won't get a proper RINEX file under these circustances\n");
   printf("Lets give it a try, just in case your GPS doesnt sent out 0x33 records\n");
   //printf("Exiting now\n");
   //fclose(f_bin);
   //exit(0);
  }
                     
}


int test_async_basic(double T_LOG, FILE *f_bin)
{
 clock_t start=clock();
 double dt;
 UINT n; 
 ULONG cont=0;
 int failed=0;
 BYTE start_async[4]={0x1C,0x02,0xff,0xff};
 BYTE stop_async[4]={0x1C,0x02,0x00,0x00};

 if (verbose) 
  printf("STARTING BASIC ASYNC TEST---------------------------------------\n");

 start=clock();

 if (open_port(PORT)==0) return 0;
 if (send_packet(start_async)==0) return 0;


 CHARS_READ=0;
 READ_TIMEOUT=1000;  //One second timeout
 do 
  {
   n=read_data(0);
   dt=((double)clock()-start)/CLOCKS_PER_SEC;   

   if (n==0) failed++;
   else
   {
	*p_error_code=0; if (CHKSUM)  { write_packet(f_bin); cont++; }
   }
   
   if (verbose) 
     printf("%6.1f secs left: %6d rcvd pcks. %2d failed reads. Current 0x%02x%c",T_LOG-dt,cont,failed,ID_PACKET,13);       	   
  }
 while (dt<T_LOG && failed<MAX_FAILED); 
 READ_TIMEOUT=100;

 if(verbose) 
  {   
   printf("                                                                           %c",13);
   printf("Comm Stats: Chars %ld (%.1f Kbit/s): %d OK records. %d failed reads\n",CHARS_READ,(double)CHARS_READ*8/(1024*dt),cont,failed);
   if (failed>=MAX_FAILED) printf("Too many failed packets. Clossing connection now\n");
  } 


 if (*p_error_code==2560)  // Timeout
 {
  close_port();
  clear_line();  
  return 0;
 }
 else    // Stop Async messages
 {
  ACK_PACKETS=0;
  
  if (send_packet(stop_async)==0) return 0;  
  pausa(1000);
#ifdef LINUX
    purge_comm(pcom); 
#else
    if (PurgeComm(pcom,PURGE_TXCLEAR | PURGE_RXCLEAR)==0) return 0;
#endif
  if (close_port()==0) return 0;
 }

 if (verbose) 
  printf("ASYNC TESTING FINISHED WITHOUT PROBLEMS------------------------\n");

 return 1;
}



int log_stream(double T_LOG, FILE *f_bin)
{
 BYTE buffer[256];
 int index;
 clock_t start;
 double dt;
 int timeouts=0;
 BYTE start_async[4]={0x1C,0x02,0xff,0xff};
 BYTE stop_async[4]={0x1C,0x02,0x00,0x00};

 if (verbose) 
  printf("DUMPING SERIAL PORT STREAM DIRECTLY TO FILE--------------------\n");

 start=clock();

 if (open_port(PORT)==0) return 0;
 ACK_PACKETS=0;
 if (send_packet(start_async)==0) return 0;

 index=0;
 timeouts=0; READ_TIMEOUT=1000;  //One second timeout
 CHARS_READ=0;
 do 
  {
  
   if(index==256) {fwrite(buffer,1,256,f_bin); index=0;} 

   if (read_char(buffer+index)==0) timeouts++; else index++;

   dt=((double)clock()-start)/CLOCKS_PER_SEC;   

   if (verbose) 
    {
     printf("%6.1f secs left: %8d rcvd bytes. ",T_LOG-dt,CHARS_READ);
     printf("%4d timeouts.%c",timeouts,13);
    }       	   
  }
 while (dt<T_LOG && timeouts<MAX_FAILED); 
 READ_TIMEOUT=100;

 // Dump remaining bytes in buffer
 if (index) fwrite(buffer,1,index,f_bin);

 if(verbose) 
  {   printf("                                                                           %c",13); 
printf("Comm Stats: Chars %ld ",CHARS_READ);
printf("(%.1f Kbit/s). ",(double)CHARS_READ*8/(1024*dt));
printf("%d timeouts\n",timeouts); 
if (timeouts>=MAX_FAILED) 
  printf("Too many timeouts. Clossing connection now\n");
 } 


 if (*p_error_code==2560)  // Timeout
 {
  close_port();
  clear_line();  
  return 0;
 }
 else    // Stop Async messages
 {
  ACK_PACKETS=0;
  
  if (send_packet(stop_async)==0) return 0;  
  pausa(1000);
#ifdef LINUX
    purge_comm(pcom); 
#else
    if (PurgeComm(pcom,PURGE_TXCLEAR | PURGE_RXCLEAR)==0) return 0;
#endif
  if (close_port()==0) return 0;
 }

 if (verbose) 
  printf("DUMPING OF SERIAL PORT STREAM FINISHED WITHOUT PROBLEMS---\n");

 return 1;
}






void log_packets_async(int flag,double T_LOG, FILE *f_bin)
{
 clock_t start=clock();
 double dt;
 UINT n; 
 ULONG cont=0;
 int failed=0;


 if (verbose) 
  printf("-----------------------------------------------------------------\n");

 start=clock();

 if (async(flag)==0) return;   // Enable Async messages

 CHARS_READ=0;
 //READ_TIMEOUT=(int)(T_LOG*1000);
 READ_TIMEOUT=1000;  //One second timeout
 do 
  {
   n=read_data(0);
   dt=((double)clock()-start)/CLOCKS_PER_SEC;   

   if (n==0) failed++;
   else
   {
	*p_error_code=0;
    if (CHKSUM)  { write_packet(f_bin); cont++; }
   }
   
   if (verbose) 
     printf("%6.1f secs left: %6d rcvd pcks. %2d failed reads. Current 0x%02x%c",T_LOG-dt,cont,failed,ID_PACKET,13);       	  
 
  }
 while (dt<T_LOG && failed<MAX_FAILED); 
 READ_TIMEOUT=100;

 if(verbose) 
  {   
   printf("                                                                           %c",13);
   printf("Comm Stats: Chars %ld (%.1f Kbit/s): %d OK records. %d failed reads\n",CHARS_READ,(double)CHARS_READ*8/(1024*dt),cont,failed);
   if (failed>=MAX_FAILED) printf("Too many failed packets. Clossing connection now\n");
  } 


 if (*p_error_code==2560)  // Timeout
 {
  close_port();
  clear_line();  
 }
 else async(0);   // Stop Async messages


 if (verbose) 
  printf("-----------------------------------------------------------------\n");

}


ULONG log_packets_request(UINT flag_request, FILE* dest)
{
 ULONG nrecords,k;
 BYTE orden[4]={0x0A,0x02,0x07,0x00};    

 orden[2]=(BYTE)(flag_request%256);  
 orden[3]=(BYTE)(flag_request/256);
  

 if (open_port(PORT)==0) return 0;        
 if (send_packet(orden)==0) return 0;
 if (read_data(1)==0) return 0;
 
 if (verbose) 
  printf("-----------------------------------------------------------------\n"); 

 write_packet(dest);
 //fwrite(INI_PACKET,L_PACKET+2,1,dest); fflush(dest);

 if (ID_PACKET!=0x1B) 
  {
   close_port();
   if (verbose) 
    {
     printf("One record received\n");
     printf("-----------------------------------------------------------------\n"); 
    }
   return 1;
  }

 
 nrecords=get_uint(DATA_PACKET);
 
 pausa(80);
 k=0;
 do
   {
    pausa(20); if (read_data(1)==0) return 0;
    if (verbose) printf("Records   : %3d expected. %3d rcvd%c",nrecords,k,13);
    write_packet(dest);
    //fwrite(INI_PACKET,L_PACKET+2,1,dest);  fflush(dest);
    k++;
   }
 while (ID_PACKET!=EOD);
 k--;
 
 if (verbose) 
  {
   printf("Records   : %3d expected. %3d actually received\n",nrecords,k);   
   printf("-----------------------------------------------------------------\n"); 
  }

 close_port();

 return (k);
}


///////////////////////////////////////
/// DISPLAY ERROR MSG
///////////////////////////////////////
int check_bit(ULONG x, BYTE pos)
{
	ULONG mask= 1 << pos;
	return (x & mask);
}

void show_err_msg(ULONG n)
{
if (n==0) { if (verbose==2) printf("No comm errors during process\n"); return;}

printf("Serial Comm Error %ld -> 0x%08lx: ",n,n); 
if (check_bit(n,0)) printf("Can't open serial port\nPossibly being used by another aplication\n");               
if (check_bit(n,1)) printf("Error in SETUP COMM port\n");
if (check_bit(n,2)) printf("Error in  GetComm\n");      
if (check_bit(n,3)) printf("Error in  SetComm\n");   
if (check_bit(n,4)) printf("Error in  GetTimeOuts\n");   
if (check_bit(n,5)) printf("Error in  SetTimeOuts\n");   
if (check_bit(n,6)) printf("Error purging COM port\n");   
if (check_bit(n,7)) printf("Error closing COM port: maybe it is already closed\n");   
if (check_bit(n,8)) printf("Hardware Error reading COMM port\n");  
if (check_bit(n,9) && check_bit(n,10))
{ 
	printf("TIMEOUT waiting for ACK\n");
	printf("GPS doesn't answer in %s: Is it on and in GRMN/GRMN mode?\n",PORT);
}    
if (check_bit(n,9) && check_bit(n,11))
{
	printf("TIMEOUT waiting for a PACKET\n");
	printf("GPS doesn't answer in %s: Is it on and in GRMN/GRMN mode?\n",PORT);
}     
if (check_bit(n,16)) printf("Hardware Error when sending data to COM port\n");
if (check_bit(n,17)) printf("Short Write in COM port\n");   
if (check_bit(n,31)) printf("Command not recognize; You should not be seeing this\n");
}


/////////////////////////////////////////////////////
// Set default values and parse user arguments
//////////////////////////////////////////////////////

void print_help()
 {
  char help[2048];
  
  sprintf(help,"-----------------------------------------------------------------\n\
* Async Software to log raw GPS data from some Garmin handhelds *\n\
* Version %4.2f    Copyright 2000,2001   Antonio Tabernero Galan *\n\
-----------------------------------------------------------------\n\
Usage:\n\
  async or async -h: shows this help\n\
  async command [options]\n\n",VERSION);


  strcat(help,"------------------- ASYNC COMMANDS ------------------------------\n\n\
  async -c : only checks port availability\n\
  async -i : only tries to get the GPS ID (default)\n\
  async -a 0xnnnn : Enable async events with hex mask nnnn\n\
  async -r 0xnnnn : Sends request type nnnn.\n\
  async -rinex : by enabling only those records relevant to the\n\
                 generation of a RINEX file you avoid missing\n\
                 observations (that can happen when there are too\n\
                 many async events coming). Use this option when you\n\
                 plan to generate a RINEX file from the collected data\n\
  async +doppler: if you're using the latest version (1.2 or newer) of\n\
                  async you can get Doppler shift data in addition to\n\
                  pseudoranges and phase using this flag instead of -rinex.\n\
                  Be warned that since there is now more data coming from\n\
                  the serial port you might start missing some observations.\n");

strcat(help,"-------------------- ASYNC OPTIONS   ---------------------------------------\n\n\
  async -p port_name : Selects serial comm port (comx, ttySx)\n\n\
                       Default is com1 (Win) or ttyS0 (Linux)\n\n\
  async -t ttt : Sets log time to ttt seconds. Default 30 sec.\n\
  async -o filename : Save received packets in filename\n\
                      By default the output goes to week_second.g12\n\n\
---------------------------------------------------------------------------\n\n\
  The usual procedure would be to find an unused comm port using\n\n\
    async -p com1 -c  or async -p com2 -c (ttyS0,ttyS1 in Linux)\n\n\
  Once you find the port, connect your GPS and check if the program sees it\n\n\
     async -p comN -i\n\n\
  If your GPS is identified you can start logging data using the\n\
    async -a -r -rinex or +doppler commands.\n\
----------------------------------------------------------------------------\n");

  printf("%s",help); exit(0); 
   

}
              

void parse_args(int argc,char** argv,BYTE *command,double* log_time,unsigned int* flag,char *fich)
{
 int k=1;
 ULONG temp;
 time_t tt;
 struct tm *gmt;
 ULONG  gps_time;
 
 if(argc==1) print_help();
 
 // Default values
 
 strcpy(PORT,DEF_PORT);   //printf("%s %s\n",PORT,DEF_PORT); getchar();
 *command=DEF_COMMAND;
 *log_time=DEF_LOG_TIME;
 *flag=DEF_FLAG;
 
 READ_TIMEOUT=100;
 verbose=1;
 
 time(&tt); gmt=gmtime(&tt);
 gps_time=(gmt->tm_sec+60*(gmt->tm_min+60*(gmt->tm_hour+24*gmt->tm_wday)));
 sprintf(fich,"%06u.g12",gps_time);
                                       
 // User provided arguments
    while (k<argc)
     {
      if (strcmp(argv[k],"-p")==0)
       { 
#ifdef LINUX
        strcpy(PORT,"/dev/"); strcat(PORT,argv[k+1]); 
#else  
        strcpy(PORT,argv[k+1]);
#endif
        k+=2; 
       }
      else if (strcmp(argv[k],"-h")==0) {print_help(); exit(0);}
      else if (strcmp(argv[k],"-i")==0) {*command=IDENT; k++;}
      else if (strcmp(argv[k],"-rinex")==0) {*command=RINEX; k++;}
      else if (strcmp(argv[k],"+doppler")==0) {*command=DOPPLER; k++;}
      else if (strcmp(argv[k],"-c")==0) {*command=CHECK; k++;}
      else if (strcmp(argv[k],"-stdout")==0) {STDOUT=1; verbose=0; k++;}
      else if (strcmp(argv[k],"-all")==0) 
	{
	 *command=LOG_ALL; *flag=0xffff; strcpy(fich,"test_all.bin"); k++; 
	}
      else if (strcmp(argv[k],"-test")==0) 
	{
         *command=TEST; *flag=0xffff; strcpy(fich,"test.bin"); k++; 
	}
      else if (strcmp(argv[k],"-a")==0)
       {
        *command=ASYNC; temp=strtoul(argv[k+1],(char**)NULL,16);
        *flag =(UINT)temp;
        k+=2;
       }
      else if (strcmp(argv[k],"-r")==0)
       {
        *command=REQST; temp=strtoul(argv[k+1],(char**)NULL,16);
        *flag= (UINT)temp;
        k+=2;
       }
      else if (strcmp(argv[k],"-q")==0) {verbose=0; k++;}
      else if (strcmp(argv[k],"-V")==0) {verbose=2; k++;}
      else if (strcmp(argv[k],"-t")==0) {*log_time=atoi(argv[k+1]); k+=2;}
      else if (strcmp(argv[k],"-o")==0) {strcpy(fich,argv[k+1]); k+=2;}
      else { printf("Unknown Option %s\n",argv[k]); k++;}
     }


    if (STDOUT==0)
    {
    printf("-----------------------------------------------------------------\n");
    printf("* Async Software to log raw GPS data from some Garmin handhelds *\n");
    printf("* Version %4.2f.   Copyright 2000,2001   Antonio Tabernero Galan *\n",VERSION);
    printf("-----------------------------------------------------------------\n");
   }
                                     // Display info
    if (verbose==2)  printf("GPS Time %6u. GMT %s",gps_time,asctime(gmt));
 
    if (verbose)
     {
      printf("Serial port: %s. Command: ",PORT);
      switch (*command)
       {
        case IDENT: printf("GPS Identification.\n");
         break;
        case CHECK: printf("Check Comm Port\n");
         break;
        case LOG_ALL:
         printf("Binary dump from serial port.\n");
         printf("Log-time %.0f sec. File: %s\n",*log_time,fich);
         break;
        case TEST:
         printf("Test async events (mask 0xffff)\nLog-time %.0f sec to file %s\n",*log_time,fich);
         break;
        case ASYNC:
         printf("Log async events (mask 0x%04x)\nLog-time %.0f sec. ",*flag,*log_time);
         printf("Output binary file %s\n",fich);
         break;
        case REQST:
         printf("Request records (type 0x%04x).\n",*flag);
         printf("Output binary file %s\n",fich);
         break;
        case RINEX:
         printf("Log async events for Rinex.\nLog-time %.0f sec. ",*log_time);
         printf("Output binary file %s\n",fich);
         break;
        case DOPPLER:
         printf("Log for Rinex (+Doppler).\nLog-time %.0f sec. ",*log_time);
         printf("Output binary file %s\n",fich);
         break;
        default: break;
       }
      printf("-----------------------------------------------------------------\n");
     }
 
}                            



void test_eph()
{
 BYTE eph[6]={0x0d,0x04,0x02,0x0c,0x00,0x00};
 UINT n;

 if (open_port(PORT)==0) return;
 if (send_packet(eph)==0) return;

 n=read_data(0);
 while(n) { printf("Leidos %d bytes\n",n); n=read_data(0); }

 if (close_port()==0) return;  
}


int main(int argc, char **argv)
{
 char fich[50];
 BYTE command;
 double log_time; 
 unsigned int flag;
 ULONG err;
 FILE *fd;


#ifdef TRACE_IO
 TRACE=fopen(TRACE_FILE,"wt");
#endif


 parse_args(argc,argv,&command,&log_time,&flag,fich);

 // Set Initial error code to 0
 err=0; p_error_code=(ULONG*)&err; 


 if (clear_line()==0) { show_err_msg(err); exit(0); }

 // Print position & date
 if ((command!=CHECK) && (command!=TEST) && (command!=LOG_ALL)) 
   { 
    get_pos(1); get_date(1); 
   }


 if ( (command!=IDENT) && (command!=CHECK) ) 
  {
   fd = (STDOUT==0)? fopen(fich,"wb"): stdout; 
  }

 switch(command)
  {
   case IDENT: ident(); break;
   case CHECK: check_port(); break;
   case TEST:	  
    if(test_async_basic(log_time,fd)==0)
    printf("THERE WAS SOME TROUBLE WHILE RUNNING THE TEST---------------\n");
    break;	
   case LOG_ALL:
     log_stream(log_time,fd);
    break; 
   case ASYNC:
    if (flag)
      {
       ident();     write_packet(fd); // fwrite(INI_PACKET,1,L_PACKET+2,fd);
       get_pos(0);  write_packet(fd);  //fwrite(INI_PACKET,1,L_PACKET+2,fd);
       get_date(0); write_packet(fd);  //fwrite(INI_PACKET,1,L_PACKET+2,fd);
       log_packets_async(flag,log_time,fd);
      }
    else async(flag);
    break;
   case REQST:
     log_packets_request(flag,fd);
   break;
   case RINEX:
     ident();     write_packet(fd); // fwrite(INI_PACKET,1,L_PACKET+2,fd);
     get_pos(0);  write_packet(fd); //fwrite(INI_PACKET,1,L_PACKET+2,fd);
     get_date(0); write_packet(fd); //fwrite(INI_PACKET,1,L_PACKET+2,fd);
     log_packets_0x33(fd);
     log_packets_async(0x0020,log_time,fd);
   break;
   case DOPPLER:
     ident();     write_packet(fd); //fwrite(INI_PACKET,1,L_PACKET+2,fd);
     get_pos(0);  write_packet(fd); //fwrite(INI_PACKET,1,L_PACKET+2,fd);
     get_date(0); write_packet(fd); //fwrite(INI_PACKET,1,L_PACKET+2,fd);            
     log_packets_0x33(fd);
     log_packets_async(0x0028,log_time,fd);
   break;
   default: 
    set_error(E_ORDEN); printf("Unknown command"); 
   break;
  }                    

 if ( (command!=IDENT) && (command!=CHECK) ) if (STDOUT==0) fclose(fd);
 

 show_err_msg(err);

 #ifdef TRACE_IO
  fclose(TRACE);
 #endif

 return 1;
}


