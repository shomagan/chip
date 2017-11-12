#!/usr/bin/python3
import sys
try:
    import msvcrt
    PLATFORM = "win"
except ImportError:
    PLATFORM = "unix"
    import termios
    from select import select
    import CHIP_IO.SERVO as SERVO
    import CHIP_IO.GPIO as GPIO
    import CHIP_IO.Utilities as UT


import socket,_thread as thread, threading
import time 
global chip_dio_inited
global receive_time
UDP_PORT_CLIENT = 8
UDP_PORT_SERVER = 7

def chip_dio_init():
    global chip_dio_inited
    chip_dio_inited = 1
    try:
        GPIO.setup("LCD-CLK",GPIO.OUT,initial=0)
        SERVO.start("CSID4",25)
        SERVO.start("CSID5",25)
    except RuntimeError:
        UT.unexport_all()
        chip_dio_deinit()
        chip_dio_inited = 1
        GPIO.setup("LCD-CLK",GPIO.OUT,initial=0)
        SERVO.start("CSID4",25)
        SERVO.start("CSID5",25)

def stop_motor():
    GPIO.output("LCD-CLK",GPIO.LOW)
    SERVO.set_angle("CSID4",25)
    SERVO.set_angle("CSID5",25)


def chip_dio_deinit():
    global chip_dio_inited
    chip_dio_inited = 0
    GPIO.cleanup("LCD-CLK")
    SERVO.stop("CSID4")
    SERVO.stop("CSID5")
    SERVO.cleanup()


def print_debug(*args):
    a = 0
    b = a

def get_ch():
    if PLATFORM == "win":
        ch = msvcrt.getch()
        return ch
    elif PLATFORM == "unix":
        return ""

def UdpList(sock):
  global chip_dio_inited
  global receive_time
  while(1):
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print_debug (addr)
    print_debug ((data),len(data))
    data_s = []
    for i in range(0,len(data)):
      data_s.append(data[i])
    if len(data_s)==1 and data_s[0]==72:
      receive_time = time.time()
      print_debug('receive /\\')
      if chip_dio_inited==0:
        chip_dio_init()
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.set_angle('CSID4',-10)
      SERVO.set_angle('CSID5', 80)
    if len(data_s)==1 and data_s[0]==80:
      receive_time = time.time()
      print_debug('receive \\/')
      if chip_dio_inited==0:
        chip_dio_init()
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.set_angle('CSID5',-10)
      SERVO.set_angle('CSID4', 80)
    if len(data_s)==1 and data_s[0]==77:
      receive_time = time.time()
      print_debug('receive ->')
      if chip_dio_inited==0:
        chip_dio_init()
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.set_angle("CSID4",5)
      SERVO.set_angle('CSID5',80)
    if len(data_s)==1 and data_s[0]==75:
      receive_time = time.time()
      print_debug('receive <-')
      if chip_dio_inited==0:
        chip_dio_init()
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.set_angle("CSID5",45)
      SERVO.set_angle('CSID4',-10)
    if len(data_s)==1 and data_s[0]==113:
      print_debug('receive quit')
      stop_motor()                                           
      if chip_dio_inited==1:
        chip_dio_deinit()                                           
      print_debug('quit')
      time.sleep(2)
      thread.exit()
      sock.close()
      sys.exit(1)
    print_debug(data_s)

if __name__ == '__main__':
    global chip_dio_inited
    global receive_time
    chip_dio_inited = 0
    UDP_IP = '127.0.0.1'
    MESSAGE = "Hello,chip!"
    print_debug ("UDP target port:", UDP_PORT_SERVER)
    print_debug (MESSAGE)
   
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", UDP_PORT_SERVER))

    thread.start_new_thread(UdpList, (sock,))
    receive_time = time.time()
    UT.unexport_all()
    while 1:
        if (receive_time + 1.0 < time.time()) and chip_dio_inited:
            receive_time = time.time()
            stop_motor()                                           

        q = get_ch()
        if q:
            print_debug(ord(q))
            if ord(q) == 99:   #c
                print_debug('socket connection')
            if ord(q) == 72:   #/\
                send_str = bytearray([72])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_CLIENT))
                print_debug('/\\')
            if ord(q) == 80:   #\/
                send_str = bytearray([80])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_CLIENT))
                print_debug('\\/')
            if ord(q) == 77:   #->
                send_str = bytearray([77])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_CLIENT))
                print_debug('->')
            if ord(q) == 75:   #<-
                send_str = bytearray([75])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_CLIENT))
                print_debug('<-')
            if ord(q) == 113:   #q
                print_debug('quit')
                chip_dio_deinit()
                time.sleep(2)
                thread.exit()
                sock.close()
                sys.exit(1)
