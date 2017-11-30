from django.shortcuts import render,HttpResponse
from app01 import models

def test(request,*args,**kwargs):


    return render(request,'test.html')