import json
import os
import time
import sys

import numpy as np
import cv2
import redis
import settings
from utils_model.get_model import get_model

from utils_model.bboxes import plot_bboxes, NMS, euristic_detection

import io
from PIL import Image
import base64


# Connect to Redis
db = redis.Redis(
                host = settings.REDIS_IP ,
                port = settings.REDIS_PORT,
                db = settings.REDIS_DB_ID
                )


# Load your ML model and assign to variable `model`
model = get_model()


def predict_bboxes(img_name, annotation_style, show_heuristic=False):
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
    # Non-Max Supression: Filter only best bounding boxes
    best_bboxes = NMS(output.xyxy[0].numpy(), overlapThresh= settings.OVERLAP_THRESH)


    # Build image name and path
    extension = '.' + img_name.split('.')[-1]
    img_base_name = img_name.split('.')[:-1]
    
    if show_heuristic:
      img_name =  ''.join(img_base_name) + '_heur' + extension
      heu_img_path = os.path.join(settings.PREDICTIONS_FOLDER, img_name)  
      if best_bboxes.size == 0:
        cv2.imwrite(heu_img_path, img_orig)
      else:
        img_heur = euristic_detection(img_orig, best_bboxes)
        cv2.imwrite(heu_img_path, img_heur)
 
    if annotation_style == 'bbox':
      img_name =  ''.join(img_base_name) + '_bbox' + extension
    else:
      img_name =  ''.join(img_base_name) + '_heat' + extension
    pred_img_path = os.path.join(settings.PREDICTIONS_FOLDER, img_name)  
    # Annotate image and stores it
    if best_bboxes.size == 0:
      cv2.imwrite(pred_img_path, img_orig)
      return img_orig
    else:
      img_pred = plot_bboxes(img_orig, box_coordinates= best_bboxes, style = annotation_style) 
      cv2.imwrite(pred_img_path, img_pred)     
      return img_pred       

def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string  = base64_string[idx+7:]

    sbuf = io.BytesIO()

    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)


    img =  cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


    # Get bounding boxes
    output = model(img)
    # Non-Max Supression: Filter only best bounding boxes
    #best_bboxes = NMS(output.xyxy[0].numpy(), overlapThresh= settings.OVERLAP_THRESH)
    img_pred = plot_bboxes(img, box_coordinates= output.xyxy[0].numpy().astype(int), style = 'bbox')


    cv2.imwrite(os.path.join(settings.PREDICTIONS_FOLDER, 'readb64.jpg'), img_pred)

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
        job_id =  job_data['id']
        is_streaming = job_data['is_streaming']
        image_name_data = job_data['image_name_data']
        annotation_style = job_data['annotation_style']
        show_heuristic = job_data['show_heuristic']

        # Predict
        if is_streaming:
          print('is_streaming')
          readb64(image_name_data)
        else:
          img_out = predict_bboxes(image_name_data, annotation_style, show_heuristic)
        
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
