from django.shortcuts import render, redirect
 
 
def base(request):
    return render(request,'base.html')

def base1(request):
    return render(request,'base1.html')

def adminbase(request):
    return render(request,'adminbase.html')