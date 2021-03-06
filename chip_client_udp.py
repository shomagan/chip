#!/c/Python3/ python
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
    UT.unexport_all()

import socket,_thread as thread, threading
import time 
chip_dio_inited = 0
def chip_dio_init():
    chip_dio_inited = 1
    GPIO.setup("LCD-CLK",GPIO.OUT,initial=0)
    SERVO.start("CSID4",25)
    SERVO.start("CSID5",25)

def chip_dio_deinit():
    chip_dio_inited = 0
    GPIO.cleanup("LCD-CLK")
    SERVO.stop("CSID4")
    SERVO.stop("CSID5")

def print_debug(content):
    print(content)
def get_ch():
    if PLATFORM == "win":
        ch = msvcrt.getch()
        return ch
    elif PLATFORM == "unix":
        fd = sys.stdin.fileno()
        old_setting = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            i, o, e = select([sys.stdin.fileno()], [], [], 5)
            if i:
                ch = sys.stdin.read(1)
            else:
                ch = ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_setting)
        return ch
    else:
        return ""

def UdpList(sock):
  while(1):
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print (addr)
    print ((data),len(data))
    data_s = []
    for i in range(0,len(data)):
      data_s.append(data[i])
    if len(data_s)==1 and data_s[0]==72:
      print_debug('receive /\\')
      if chip_dio_inited==0:
        chip_dio_init()
      SERVO.set_angle('CSID4',-10)
      SERVO.set_angle('CSID5', 60)
    if len(data_s)==1 and data_s[0]==80:
      print_debug('receive \\/')
      if chip_dio_inited==0:
        chip_dio_init()
      SERVO.set_angle('CSID5',-10)
      SERVO.set_angle('CSID4', 60)
    if len(data_s)==1 and data_s[0]==77:
      print_debug('receive ->')
      if chip_dio_inited==0:
        chip_dio_init()
      SERVO.set_angle('CSID4',25)
      SERVO.set_angle('CSID5',60)

    if len(data_s)==1 and data_s[0]==75:
      print_debug('receive <-')
      if chip_dio_inited==0:
        chip_dio_init()
      SERVO.set_angle('CSID4',25)
      SERVO.set_angle('CSID5',60)

    if len(data_s)==1 and data_s[0]==113:
      print_debug('receive quit')
      if chip_dio_inited==1:
        chip_dio_deinit()                                           

    print_debug(data_s)

if __name__ == '__main__':
    UDP_IP = '192.168.88.218'
    UDP_PORT_CLIENT = 8
    UDP_PORT_SERVER = 7
    MESSAGE = "Hello,chip!"
    print ("UDP target port:", UDP_PORT_SERVER)
    print (MESSAGE)
   
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind(("", UDP_PORT_CLIENT))

    thread.start_new_thread(UdpList, (sock,))
    receive_time = time.time()
    while 1:
        q = get_ch()
        if q:
            print(ord(q))
            if ord(q) == 99:   #c
                print('socket connection')
            if ord(q) == 72:   #/\
                send_str = bytearray([72])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_SERVER))
                print('/\\')
            if ord(q) == 80:   #\/
                send_str = bytearray([80])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_SERVER))
                print('\\/')
            if ord(q) == 77:   #->
                send_str = bytearray([77])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_SERVER))
                print('->')
            if ord(q) == 75:   #<-
                send_str = bytearray([75])
                sock.sendto(send_str,(UDP_IP, UDP_PORT_SERVER))
                print('<-')
            if ord(q) == 113:   #q
#                send_str = bytearray([113])
 #               sock.sendto(send_str,(UDP_IP, UDP_PORT_SERVER))
                print('quit')
                time.sleep(2)
                thread.exit()
                sock.close()
                sys.exit(1)
            if receive_time > time.time() + 1.0 and chip_dio_inited:
                chip_dio_deinit()                                           
