from django.shortcuts import render, redirect
from store.views import *
from store.models import *
from django.contrib.auth.models import User
from .models import Profile
import random
import http.client
from django.conf import settings
from django.contrib.auth import authenticate, login, authenticate

from django.contrib.auth.forms import AuthenticationForm




def send_otp(mobile , otp):
    print("FUNCTION CALLED")
    url = "http://apismpp.ajuratech.com/sendtext"

    querystring = {"apikey":"a6584c5c4908024d","secretkey":"80b5d891","callerID":"quickcartbd","toUser":mobile,"messageContent":"Your otp is "+otp }
    headers = {
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response)
    return None



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