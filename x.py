from email.message import EmailMessage
import smtplib
import ssl

ems='explorepallivasalgp@gmail.com'
emp='aapnsstawfopxmle'
emr='akshaysnairunni@gmail.com'

subject='Hello'
body='''
this is a test mail
'''
em=EmailMessage()
em['From']=ems
em['To']=emr
em['Subject']=subject
em.set_content(body)

c=ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com',465,context=c) as smtp:
    smtp.login(ems,emp)
    smtp.sendmail(ems,emr,em.as_string())