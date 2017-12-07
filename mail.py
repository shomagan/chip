import smtplib
import ipgetter


def main():

    fromaddr = 'shomagan@gmail.com'
    toaddrs  = 'shomagan@gmail.com'
    IP = ipgetter.myip()
    msg = IP
    username = 'shomagan@gmail.com'
    password = ''
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

if __name__ == "__main__":
    main()
