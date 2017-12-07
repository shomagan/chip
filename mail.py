import smtplib

def main():

    fromaddr = 'shomagan@gmail.com'
    toaddrs  = 'shomagan@gmail.com'
    msg = 'Why,Oh why!'
    username = 'shomagan@gmail.com'
    password = ''
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

if __name__ == "__main__":
    main()
