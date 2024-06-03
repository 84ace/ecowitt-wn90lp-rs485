"""
example:
python3 ecowitt-wn90lp-rs485.py
payload:  b"\x119\x00\x1e\x02u\x00+\x00\x00\x00\x00\x00\x96\x00\x00'"
int values:  [4409, 30, 629, 43, 0, 0, 150, 0, 39]
Light (Lux): 44090, UVI %: 3.0, Temperature (C): 22.900000000000002, Humidity %: 43, Wind Speed (m/s): 0.0, Gust Speed (m/s): 0.0, Wind Direction: 15.0, Rainfall (/12h): 0.0, ABS Pressure (hPa): 3.9000000000000004
"""

# to install PySerial: python -m pip install pyserial
import serial

ser = serial.Serial(
    port='/dev/tty.wchusbserial1120',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=5
)

# Construct the Modbus message to read a register
# This grabs the first 7 registers
message = (0x90, 0x03, 0x01, 0x65, 0x00, 0x09, 0x88, 0xAE)

# from https://osswww.ecowitt.net/uploads/20231122/WS90ModbusRTU_V1.0.5_En.pdf
# 0165: Light: value*10 (Range: 0lux -> 300,000lux), If invalid fill with 0xFFFF
# 0166: UVI: RO Value in hex Uvi=UVIvalue/10 (Range: 0 -> 150), If invalid fill with0xFFFF
# 0167: Temperature: RO Value in hex 10.5 C = 1F9h -10.5 C = 127h with 400 offset added(Range: -40.0C -> 60.0C) If invalid fill with0xFFFF
# 0168: Humidity RO data in hex (Range: 1% - 99%), If invalid fill with0xFFFF
# 0169: Wind Speed RO Value in hex, If invalid fill with0xFFFF.Wind Speed =WIND value*0.1m/s(0~40m/s)
# 016A: Gust Speed RO Value in hex, If invalid fill with0xFFFF.Gust Speed =GUST value*0.1m/s(0~40m/s)
# 016B: Wind Direction RO Value in hex (Range: 0°- 359°), If invalid fill with0xFFFF
# 016C: Rainfall RO Value in hex Rain = value*0.1mm1.8mm=12H
# 016D: ABS Pressure RO Value in hex ABS = value*0.1hPa1002.6hPa=272AH, If invalid fill with0xFFFF
# 016E: RainCounter RO data in hex Rain = value*0.01mm0.18mm=12H

# Send the message to the device
ser.write(message)

# Read the response
response = ser.readline()

# Close the connection
ser.close()

# Extract the data from the response
data = response[3:-2]

print("payload: ",data)

# Convert the data to a list of integers
values = [int.from_bytes(data[i:i+2], byteorder='big', signed=False) for i in range(0, len(data), 2)]

print("int values: ", values)

# Extract values
light = values[0]
light = light*10 # Range: 0lux -> 300,000lux

uvi = values[1]
uvi = uvi/10 # Range: 0 -> 150

temperature = values[2] 
temperature = (temperature-400)*.1 # RO Value in hex 10.5 C = 1F9h -10.5 C = 127h with 400 offset added(Range: -40.0C -> 60.0C)

humidity = values[3] 
humidity = humidity # RO data in hex (Range: 1% - 99%)

windS = values[4] 
windS = windS*.1 # Wind Speed =WIND value*0.1m/s(0~40m/s)

gustS = values[5] 
gustS = gustS*.1 # Wind Speed =WIND value*0.1m/s(0~40m/s)

windD = values[6] 
windD = windD*.1 # (Range: 0°- 359°)

rain = values[7] 
rain = rain*.1 # mm / 12h

press = values[8] 
press = press*.1 # mm / 12h

print("Light (Lux): {}, UVI %: {}, Temperature (C): {}, Humidity %: {}, Wind Speed (m/s): {}, Gust Speed (m/s): {}, Wind Direction: {}, Rainfall (/12h): {}, ABS Pressure (hPa): {}".format(light, uvi, temperature, humidity, windS, gustS, windD, rain, press))