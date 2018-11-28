#SMTPLIB Module defines SMTP client session object that can be used to send email to any internet machine with an SMTP.
#Create SMTP object
import smtplib
from email.mime.text import MIMEText
from email.header import Header 

def email(texttoemail):
	#Variables.
	msg = MIMEText(texttoemail, 'plain','utf-8')
	#smtp_host = 'smtp.gmail.com'
	#login, password = "xxx@gmail.com","#######"

	smtp_host = '####'
	login, password = "####"

	recipients_emails = ['#####']
	print("INSIDE EMAIL")
	msg['Subject']=Header('Vlan Config Info','utf-8')

	msg['From']=login
	msg['To']=", ".join(recipients_emails)
	print(msg)

	print("EXECUTING EMAIL CODE")
	
	s=smtplib.SMTP(smtp_host, 587, timeout=10)
	s.set_debuglevel(1)
	try:
		s.starttls()
		s.login(login,password)
		s.sendmail(msg['From'],recipients_emails, msg.as_string())
	finally:
		s.quit()
