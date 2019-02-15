AMIGOS WXT520 Weather and Location Data in Single Burst Data (SBD) files.
Terry Haran now retired and replaced by Bruce Wallin
wallinb@nsidc.org
2017/12/28

Directory is:

ftp://sidads.colorado.edu/pub/incoming/wallinb/amigos/

Filenames are of the form: amigosN_sbd.txt which contains all current
                           year-to-date hourly single burst data (sbd).

                           amigosN_wxt_24.txt which contains the most
                           recent 24 hours of hourly weather (wxt) data.

			   amigosN_wxt_YYYY.txt which contains a year's
                           worth of data for year YYYY.

    N is amigos number 1-6.
      amigos1 - Matienzo Base         64d 58.57' S
                                      60d 04.19' W =
                                      -64.9762 -60.0699    30 m asl
                amigos1 was moved from Marambio to Matienzo 2016/09/12.
      amigos2 - NSIDC roof in Boulder 40d  0.75' N
                                     105d 15.18' W =
                                      40.0125 -105.2530  1624 m asl
                amigos2 has not been heard from since 2017/10/26,
                and is now damaged and stored in the NSIDC radar lab.
      amigos3 - Lower Flask Glacer    65d 46.63' S
                                      62d 14.15' W =
                                      -65.7771 -62.6859   406 m asl
                amigos3 has not been heard from since 2015/03/08.
      amigos4 - Scar Inlet Ice Shelf  65d 46.35' S
                                      61d 54.41' W =
                                      -65.7725 -61.9068    46 m asl
                amigos4 has not been heard from since 2017/08/23.
      amigos5 - Bruce Plateau         66d 01.95' S
                Site Beta             64d 02.45' W =
                                      -66.0325 -64.0409  1976 m asl  
                amigos5 has not been heard from since 2010/07/20.
      amigos6 - Cape Disappointment   65d 33.98' S
                                      61d 44.88' W =
                                      -65.5664 -61.7480   234 m asl
                amigos6 was removed from Cape Disappintment 2017/12/02,
                and is currently enroute from Rothera Base to NSIDC Boulder
                via Punta Arenas.

Weather records:

Fields:  1       2   3      4      5   6   7     8   9     10   11  12 
Example: amigos3 WXT 102714 155001 106 5.2 -9.9 88.5 927.8 13.9 119 6.0

Fields:  13  14    15   16    17   18    19
Example: 1.3 -10.9 13.6 0.104 -5.1 0.663 0.822

1 : amigosN as in the filename
    amigos3 - Lower Flask Glacer
2 : Field Identifier
    WXT indicates WXT520 weather data
3:  Acquisition UTC Date mmddyy
    102714 = October 27, 2014
4:  Acquisition UTC Time hhmmss
    155001 = 15 hours, 50 minutes, 01 seconds
5 : Wind Direction in degrees clockwise from north
    106 degrees = from east south east
6 : Wind Speed in meters per second
    5.2 m/sec = 11.6 mph = 10.1 knots = 17.1 ft/sec = 18.7 km/hr
7 : Air Temperature in degrees C
    -9.9 C = 14.18 F
8 : Relative Humidity in percent
    88.5 % @ -9.9 C and 927.8 millibars implies dewpoint = -11.44 C
9 : Atmospheric Pressure (uncorrected for elevation)
    927.8 millibars = 927.8 hPa = 27.4 in Hg
10: WXT520 Supply Voltage in volts
    13.9 volts
11: Wind Gust Direction in degrees clockwise from north
    119 degrees = from southeast
12: Wind Gust Speed in meters per second
    6.0 m/sec = 13.4 mph = 11.7 knots = 19.7 ft/sec = 21.6 km/hr
13: WXT520 Heater Voltage
    1.3 volts (indicates heater is off)
14: WXT520 Heater Temperature in degrees C
    -10.9 C = 12.38 F
15: CPU Panel Voltage in volts
    13.6 volts
16: CPU Panel Current in amperes
    0.104 amps
17: CPU Panel Temperature in degrees C
    -5.1 C = 23.0 F
16: Downward Sun Sensor in volts
    0.663 volts
17: Upward Sun Sensor in volts
    0.822 volts @ 0.663 downward implies albedo = 0.807
NOTE: Downward Sun Sensor on amigos4 is reporting 0.0 volts as of 2014/08/08.
NOTE: Upward Sun Sensor on amigos1 has always reported  approximatedly 0.0 volts
      since first installed at NSIDC 2009/12/17.

GPS records have field identifiers of GRS, ALT, or GPS.

Campbell data logger records have field identifier CSI.
