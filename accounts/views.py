from django.shortcuts import render, redirect
from modelTraining.views import *
from modelTraining.models import *
from django.contrib.auth.models import User
from .models import Profile
import random
import http.client
from django.conf import settings
from django.contrib.auth import authenticate, login, authenticate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.contrib.auth.forms import AuthenticationForm



def send_otp(email, otp):
    # Sender email credentials
    sender_email = "gishtiyatiqe033@gmail.com"
    sender_password = "avjm jxtc ethk utur"

    # Recipient email
    recipient_email = email

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For Gmail

    # Create a secure SSL context
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "Your OTP"
        message.attach(MIMEText(f"Aicamer.com\nYour OTP is: {otp}", 'plain'))

        # Send email
        server.sendmail(sender_email, recipient_email, message.as_string())
        print("OTP email sent successfully")
    except Exception as e:
        print(f"Error sending OTP email: {e}")
    finally:
        server.quit()



def login_attempt(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        
        user = Profile.objects.filter(mobile = mobile).first()
        
        if user is None:
            user = User(username = mobile )
            user.save()
            otp = str(random.randint(1000 , 9999))
            kalaa = User.objects.get(username = mobile)
            profile = Profile(user = kalaa , mobile=mobile , otp = otp) 
            profile.save()
            send_otp(mobile, otp)
            request.session['mobile'] = mobile
            return redirect('login_otp')
        
        otp = str(random.randint(1000 , 9999))
        user.otp = otp
        user.save()
        send_otp(mobile , otp)
        request.session['mobile'] = mobile
        return redirect('login_otp')        
    return render(request,'account/login.html')





def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            user = User.objects.get(id = profile.user.id)
            login(request , user)
            return redirect('home')
        else:
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'account/login_otp.html' , context)
    
    return render(request,'account/login_otp.html' , context)
    
def resend_otp(request, mobile):
    print("called data!")
    mobile = mobile
    otp = str(random.randint(1000 , 9999))
    user = Profile.objects.filter(mobile = mobile).first()
    user.otp = otp
    print(user.otp)
    user.save()
    send_otp(mobile , otp)
   
    
    return redirect('login_otp') 
    
    

def otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            return redirect('home')
        else:
            
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'account/otp.html' , context)
            
        
    return render(request,'account/otp.html' , context)
