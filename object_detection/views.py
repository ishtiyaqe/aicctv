# views.py
import os
import threading
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .models import DownloadedFile
import os
import json
from ultralytics import YOLO
from django.core.files import File
from roboflow import Roboflow
from django.http import JsonResponse
import subprocess
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect


def execute_command_page(request):
    kl = DownloadedFile.objects.last()
    
    # Retrieve the stored string values from the model
    rf_code = kl.rf
    project_code = kl.project
    dataset_code = kl.dataset
    
    # Execute the stored code using eval()
    rf = eval(rf_code)
    project = eval(project_code)
    dataset = eval(dataset_code)
    
    # Call the dataset function if it is callable
    if callable(dataset):
        dataset_result = dataset()  # Execute the dataset function
    else:
        dataset_result = "Data process download complete"
    
    # Print the dataset result
    print(dataset_result)
    
    # Add the necessary context data and render your template
    context = {
        'dataset_result': dataset_result,
        'project_code': project_code,
        'dataset_code': dataset_code,
    }
    return render(request, 'downloaded_files.html', context)



import yaml

def extract_names_from_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
        if 'names' in data:
            return data['names']
        else:
            return []



def staff_or_admin_check(user):
    return user.is_staff or user.is_superuser

def custom_logout(request):
    logout(request)
    return redirect('admin:login')  # Redirect to the login page

def account_logout(request):
    logout(request)
    return redirect(index)  # Redirect to the login page


@login_required
@user_passes_test(staff_or_admin_check)
def index(request):
    return render(request, 'Homepage.html', )

def train_yolo(request):
    kl = DownloadedFile.objects.last()
    counts = RunNumberOfTest.objects.last()
    stat = NewModelTrainingStatus()
    

    def start_training():
        v = str(kl.project_version)
        k = kl.project_name
        data_path = os.path.join(r"C:\\Users\\gisht\\Desktop\\web\\aicctv", f"{k}-{v}")
        train_path = os.path.join(data_path, 'train')
        valid_path = os.path.join(data_path, 'valid')
        test_path = os.path.join(data_path, 'test')
        yaml_path = os.path.join(data_path, 'data.yaml')
        
        folder_path = 'runs/detect'
        # Get a list of all directories in the specified path
        directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

        # Filter out directories that start with "train"
        train_folders = [d for d in directories if d.startswith('train')]

        # Print the number of train folders
        print("Number of train folders:", len(train_folders))
        psl = len(train_folders) + 1
        kls = "train" + str(psl)
        pbl = NewModelTrainingStatus.objects.filter(Test_name = kls)
        if not pbl:
            stat.Test_name = kls
            stat.status = "Running"
            stat.save()
        else:
            return HttpResponse("Training started in the background. Please wait for the results.")
        model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)

        # Ensure all paths exist
        for path in [train_path, valid_path, test_path, yaml_path]:
            if not os.path.exists(path):
                print(f"Error: Path {path} does not exist.")
                return
        
        # Extract class names from YAML file
        class_names = extract_names_from_yaml(yaml_path)
        if not class_names:
            print("Error: No class names found in YAML file.")
            return

  
        # Prepare YAML data for YOLO training
        ppe_data = {
            'train': train_path,
            'val': valid_path,
            'test': test_path,
            'nc': len(class_names),
            'names': class_names
        }
        
        # Write YAML data to file
        with open('ppe_data.yaml', 'w') as output:
            yaml.dump(ppe_data, output, default_flow_style=True)
        # Train the model
        model.train(data='ppe_data.yaml', epochs=counts.count, imgsz=640)
        folder_path = 'runs/detect'
        # Get a list of all directories in the specified path
        directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

        # Filter out directories that start with "train"
        train_folders = [d for d in directories if d.startswith('train')]

        # Print the number of train folders
        print("Number of train folders:", len(train_folders))
        td = "train"+str(len(train_folders))
        folder_path = f'runs/detect/{td}/weights/best.pt'
        with open(folder_path, 'rb') as file:
            # Create a File object using Django's File class
            trained_model_file = File(file)
            
            # Create an instance of the Trained_model model and save the file
            trained_model_instance = Trained_model.objects.create(Test_name=td)
            trained_model_instance.Trained_model.save(os.path.basename(folder_path), trained_model_file)
                
            pbls = NewModelTrainingStatus.objects.get(Test_name = td)
            pbls.Status = "Completed"
            pbls.save()
        

    # Start the training process in a separate thread
    thread = threading.Thread(target=start_training)
    thread.start()
    folder_path = 'runs/detect'
    # Get a list of all directories in the specified path
    directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

    # Filter out directories that start with "train"
    train_folders = [d for d in directories if d.startswith('train')]

    # Print the number of train folders
    print("Number of train folders:", len(train_folders))
    psl = len(train_folders) + 1
    kls = "train" + str(psl)
    try:
        pbl = NewModelTrainingStatus.objects.get(Test_name = kls)
        status = pbl.status
        
    except NewModelTrainingStatus.DoesNotExist:
       status = "Running"
    rt = RunNumberOfTest.objects.last()
    rtf = rt.count
    context = {
        'Test_name': kls,
        'Status': status,
        'Total_count': rtf,
    }
    # Return a response to prevent a timeout error
    return render(request, 'model_training.html',context )



