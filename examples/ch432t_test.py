# -*- coding: utf_8 -*-
'''!
  @file  ch432t_demo.py
  @brief  这是一个测试demo: 把树莓派扩展板的一个modbus接口作为主机, 另一个作为从机
  @n  将它们相互连接起来, 运行这个demo就可以进行应该简单的收发测试
  @copyright  Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license  The MIT License (MIT)
  @author  [qsjhyy](yihuan.huang@dfrobot.com)
  @version  V1.0
  @date  2021-10-28
  @url  https://github.com/DFRobot/DFRobot_CH432T
'''
from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import time
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

from DFRobot_CH432T import *   # Import DFRobot_CH432T replace importing serial library


''' 
  # @brief Except replacing
  #  PORT="/dev/ttyAMA0"#serial number
  #  ser = serial.Serial(port=PORT, baudrate=115200, bytesize=8, parity='N', stopbits=1)
  #  to the following, other modbus_tk operations will be almost the same
  # @note  Serial number (actually use Raspberry Pi 'spidev0.0'), "CH432T_PORT_1" or "CH432T_PORT_2" can be used
'''
PORT_1="CH432T_PORT_1"
slave_ser = DFRobot_CH432T(port=PORT_1, baudrate=115200, bytesize=8, parity='N', stopbits=1)

PORT_2="CH432T_PORT_2"
master_ser = DFRobot_CH432T(port=PORT_2, baudrate=115200, bytesize=8, parity='N', stopbits=1)


def main():
  print('This is a self-test demo, make sure you have connected the two Modbus interfaces together correctly !\r\n')

  slave_addr = 0x66   # Address of the slave
  slave_baudrate = 115200   # Baud rate of the slave
  reg_length = 0   # 从机寄存器数据长度
  test_count = 0   # 测试次数

  """ 初始化从机 """
  print("Initializing the slave port...")
  print("slave_ser.name = %s\r\n" % slave_ser.name)
  server = modbus_rtu.RtuServer(slave_ser)
  server.start()
  slave = server.add_slave(slave_addr)
  slave.add_block('test', cst.HOLDING_REGISTERS, 0, 10)   # 设置从机寄存器

  values = [7, 1, 5]
  reg_length = len(values)
  slave.set_values('test', 0, values)   # 设置从机寄存器值
  test_values = slave.get_values('test', 0, reg_length)
  if values != list(test_values):
    print("Failed to set the slave register value!!!\r\n")

  """ 初始化主机 """
  print("Initializing the master port...")
  print("master_ser.name = %s\r\n" % master_ser.name)
  master = modbus_rtu.RtuMaster(master_ser)
  master.open()
  master.set_timeout(5.0)
  master.set_verbose(True)

  while True:
    test_count +=  1
    values = [9, 9, test_count, 9, 9]   # 注意保持寄存器是16bits, 所以最大可存储的test_count为65535
    slave.set_values('test', 0, values)   # 从机自己更改寄存器值
    reg_length = len(values)
    print('Slave test value: %d' % test_count)

    master_ser.baudrate = slave_baudrate   # Change communication baud rate to the temperature sensor baud rate 9600

    # """
    #   # Read the data of input register 0x00 of the slave whose rs485 address is 0x66
    #   # |       66       |        06      |       00 01      |      00 01       |    60 39   |
    #   # | Device address | operation code | register address | read data length | check code |
    # """
    data = master.execute(slave_addr, cst.READ_HOLDING_REGISTERS, 0, reg_length)   # 主机读取从机寄存器值
    print('Master reads data packets: %s\r\n' % (str(data)))

    time.sleep(1)


if __name__ == "__main__":
  main()
