import json
import os
import time
import sys

import numpy as np
import pandas as pd
import cv2
import redis
import settings
from utils_model.get_model import get_model

from utils_model.bboxes import plot_bboxes, NMS, euristic_detection

# Connect to Redis
db = redis.Redis(
                host = settings.REDIS_IP ,
                port = settings.REDIS_PORT,
                db = settings.REDIS_DB_ID
                )


# Load your ML model and assign to variable `model`
model = get_model()


def predict_bboxes(img_name, annotation_style):
    """
    Loads the original image and logs the new image
    with the bounding boxes. It stores it a new folder
    called response. 

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Load original image
    orig_img_path = os.path.join(settings.UPLOAD_FOLDER,img_name)
    img_orig = cv2.imread(orig_img_path)
    
    # Get bounding boxes
    output = model(img_orig)
    df = output.pandas().xyxy[0]
    # df = df.sort_values("class")
    bboxes = df[["xmin","ymin","xmax","ymax","class"]]
    # Non-Max Supression: Filter only best bounding boxes
    best_bboxes = NMS(bboxes.to_numpy(), overlapThresh= settings.OVERLAP_THRESH)
    
    # Build image name and path
    extension = '.' + img_name.split('.')[-1]
    img_base_name = img_name.split('.')[:-1]
    
    img_eur = euristic_detection(orig_img_path, best_bboxes)

    ## 1. BBox
    img_name1 =  ''.join(img_base_name) + '_bbox' + extension
    pred_img_path = os.path.join(settings.PREDICTIONS_FOLDER, img_name1)  
    # Predict (draw all bounding boxes) and store
    img_pred = plot_bboxes(orig_img_path, box_coordinates= best_bboxes, style = annotation_style) 
    cv2.imwrite(pred_img_path, img_eur)                    # store as: "predictions/<img_name_bbox.jpg>"
    
    ## 2. Heatmap 
    img_name2 =  ''.join(img_base_name) + '_heat' + extension
    pred_img_path = os.path.join(settings.PREDICTIONS_FOLDER, img_name2)  
    # Predict (draw all bounding boxes with heatmp) and store
    img_pred = plot_bboxes(orig_img_path, box_coordinates= best_bboxes, style = annotation_style) 
    cv2.imwrite(pred_img_path,img_pred)                    # store as: "predictions/<img_name_heatmap.jpg>"
                        

def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        
        # Read the job from Redis
        _ , job_data_str= db.brpop(settings.REDIS_QUEUE)
        
        # Decode image_name
        job_data = json.loads(job_data_str.decode('utf-8'))
        img_name = job_data['image_name']
        job_id =  job_data['id']
        annotation_style = job_data['annotation_style']
        
        # Predict
        predict_bboxes(img_name, annotation_style)
        
        pred_dict = {
                    "mAP": "[TO BE IMPLEMENTED]",
                    }
        
        # Store in Redis
        db.set(job_id,json.dumps(pred_dict))

        # Don't forget to sleep for a bit at the end
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
