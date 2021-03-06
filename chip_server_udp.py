#!/usr/bin/python3
import sys
old_stdout = sys.stdout
log_file = open("message.log","w")
sys.stdout = log_file

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
global command_last
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
        GPIO.setup("LCD-CLK",GPIO.OUT,initial=0)
        SERVO.start("CSID4",25)
        SERVO.start("CSID5",25)

def stop_motor():
    global command_last
    GPIO.output("LCD-CLK",GPIO.LOW)
    SERVO.stop("CSID4")
    SERVO.stop("CSID5")
    SERVO.cleanup()
    command_last = 0


def chip_dio_deinit():
    global chip_dio_inited
    chip_dio_inited = 0
    GPIO.cleanup("LCD-CLK")
    SERVO.stop("CSID4")
    SERVO.stop("CSID5")
    SERVO.cleanup()
    UT.unexport_all()



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
  global command_last
  command_last = 0
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
      if command_last:
        stop_motor()
      command_last = 72
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.start("CSID4", -35)
      SERVO.start("CSID5", 60)


    if len(data_s)==1 and data_s[0]==80:
      receive_time = time.time()
      print_debug('receive \\/')
      if chip_dio_inited==0:
        chip_dio_init()
      if command_last:
        stop_motor()

      command_last = 80
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.start('CSID5',-35)
      SERVO.start('CSID4', 60)
    if len(data_s)==1 and data_s[0]==77:
      receive_time = time.time()
      print_debug('receive ->')
      if chip_dio_inited==0:
        chip_dio_init()
      if command_last:
        stop_motor()

      command_last = 77
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.start("CSID4",60)
      SERVO.start('CSID5',60)
    if len(data_s)==1 and data_s[0]==75:
      receive_time = time.time()
      print_debug('receive <-')
      if chip_dio_inited==0:
        chip_dio_init()
      if command_last:
        stop_motor()

      command_last = 75
      GPIO.output("LCD-CLK",GPIO.HIGH)
      SERVO.start("CSID5",-60)
      SERVO.start('CSID4',-60)
    if len(data_s)==1 and data_s[0]==113:
      print_debug('receive quit')
      stop_motor()                                           
      if chip_dio_inited==1:
        chip_dio_deinit()                                           
      print_debug('quit')
      time.sleep(2)
      thread.exit()
      sock.close()
      sys.stdout = old_stdout
      log_file.close()
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
    while 0:
        if (receive_time + 0.8 < time.time()) and chip_dio_inited:
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
