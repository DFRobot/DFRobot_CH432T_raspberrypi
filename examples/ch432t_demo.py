# -*- coding: utf_8 -*-
'''!
  @file  ch432t_demo.py
  @brief  The demo shows how to use ch432t Raspberry Pi SPI to modbus expansion board that aims to convert Raspberry Pi's SPI to two modbus interfaces 
  @n  Make few modifications on the original modbus_tk, then your modbus sensors are ready to go.
  @n  The example below shows how to use the relay and temp&humid sensor connected to the board's modbus interface. 
  @copyright  Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license  The MIT License (MIT)
  @author  [qsjhyy](yihuan.huang@dfrobot.com)
  @version  V1.0
  @date  2022-09-24
  @url  https://github.com/DFRobot/DFRobot_CH432T
'''
from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import time

import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

from DFRobot_CH432T import *   # Import DFRobot_CH432T replace importing serial library

addr_sensor = 0x02   # Address of temperature and humidity sensor
addr_relay  = 0x01   # Address of the relay
threshold   = 28   # Temperature threshold
sensor_baudrate = 9600   # Baud rate of temperature and humidity sensor
relay_baudrate = 115200   # Baud rate of the relay

''' 
  # @brief Except replacing
  #  PORT="/dev/ttyAMA0"#serial number
  #  ser = serial.Serial(port=PORT, baudrate=115200, bytesize=8, parity='N', stopbits=1)
  #  to the following, other modbus_tk operations will be almost the same
  # @note  Serial number (actually use Raspberry Pi 'spidev0.0'), "CH432T_PORT_1" or "CH432T_PORT_2" can be used
'''
PORT="CH432T_PORT_1"
ser = DFRobot_CH432T(port=PORT, baudrate=115200, bytesize=8, parity='N', stopbits=1)

def main():
  print("This is a demo of how to use a Modbus sensor.")
  print("If you want it to work, make sure you have connected your Modbus device and changed the relevant parameters in the demo to those of your device!\r\n")

  # Configure serial port
  master = modbus_rtu.RtuMaster(ser)
  master.set_timeout(5.0)
  master.set_verbose(True)
  print("ser.name = ", ser.name)

  try:
    while True:
      ser.baudrate = sensor_baudrate   # Change communication baud rate to the temperature sensor baud rate 9600
      """
        # Read the data of input register 0x01 of the temperature and humidity sensor whose rs485 address is 0x02
        # |    02   |   04   |   00 01   |   00 01   | 60 39 |
        # | Device address | operation code | register address | read data length | check code |
      """
      data = master.execute(addr_sensor, cst.READ_INPUT_REGISTERS, 1, 1)
      temperature = data[0]/10   # The read 16bit data divided by 10, then you get the measured temperature data of the sensor
      print("temperature = ", temperature)
      time.sleep(3)

      ser.baudrate = relay_baudrate   # Change communication baud rate to the relay baud rate 115200
      """
        # When temperature exceeds the threshold, the relay is off
        # Write single coil register of the relay whose rs485 address is 0x01
        # |    01   |   05   |   00 00   |   FF 00   | 60 39 |
        # | Device address | operation code | register address | switching value data | check code |
        # When switching value data is 1 write: FF 00, when it is 0 write: 00 00
      """
      if temperature > threshold:
        master.execute(addr_relay, cst.WRITE_SINGLE_COIL, 0, output_value = 0 )   # 0 means the relay is disconnected, actually send data 00 00
      else:
        master.execute(addr_relay, cst.WRITE_SINGLE_COIL, 0, output_value = 1 )   # 1 means the relay is connected, actually send data FF 00
      time.sleep(3)

  except Exception as err:
    print(str(err))


if __name__ == "__main__":
  main()
