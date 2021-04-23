from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

# Create your views here.

def showUploadFile(request):

    return render(request,'files.html')


def uploadFile(request):

    archivoCargado = request.FILES['mi_archivo']
    print(archivoCargado)

    sistemaArchivos = FileSystemStorage() #('media/1/2')
    sistemaArchivos.save('RDC01_' + archivoCargado.name,archivoCargado)

    print(sistemaArchivos.location)
    print(sistemaArchivos.base_location) #media/1/2
    print(sistemaArchivos.base_url)
   

    return redirect('files')




