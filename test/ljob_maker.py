import time
import json
import cv2
import os
import shutil
from multiprocessing import Process
import numpy as np
model_type_dict = {
    0:"human",
    1:"face/detect",
    2:"silhouette",
    3:"skeleton",
    4:"pc/SSD512"
}

# ----------------- YOU ONLY NEED TO SET HERE ----------------- #
model_mode = 0 # check model_type_dict above 

template_ljob = {
        "FunctionName":"human", # change this
        "FrameIndex":"", 
        "Timestamp":"", 
        "AnalysisFeature":"Climb",
        "Sn":0, 
        "Fn":"", 
        "Pid" : -1,
        "ReturnQueue":1 # change this
    }
# template_ljob["ImageGroup"] = [ \
#             "/mnt/TrainingMachine/Training_data/HD/SaaS_HD_Data/quality_dirs/sample_by_job/data4_data2_data2_07_7f1061074a5f43708e487476d90f926a_2022_07-08_17_abe1d0196917_H21032076-human-4_ALCBICHP22231213_21032076_4.jpg", \
#             "/mnt/TrainingMachine/Training_data/HD/SaaS_HD_Data/quality_dirs/sample_by_job/data4_data2_data2_07_7f1061074a5f43708e487476d90f926a_2022_07-08_17_abe1d0196917_H21032076-human-4_ALCBICHP22231213_21032076_5.jpg", \
#             "/mnt/TrainingMachine/Training_data/HD/SaaS_HD_Data/quality_dirs/sample_by_job/data4_data2_data2_07_7f1061074a5f43708e487476d90f926a_2022_07-08_17_abe1d0196917_H21032076-human-4_ALCBICHP22231213_21032076_6.jpg" \
#         ]
# template_ljob["ZoomIn"] = [ \
#             { \
#                 "topLeft" : [0.35, 0], \
#                 "bottomRight" : [0.7, 0.3] \
#             } \
#         ]
template_ljob["SubFeature"] = {
            "InvasionMagnifier": {
                "Points": [
                        { "x": 0.5,"y": 0.0}
                ]
            }
        }
# video_path = "/home/ubuntu/evaluationVideo.mp4" 
video_path = "/mnt/HD/tmp/repeat_vid2.mp4" 

# video_path = "/mnt/nas2_2/DemoVideo3/201001_hsinchu/e56990cc7d654d6fabda342b2e3cbe30/concat/10-11/13/201011_134023_10m8s-1602423623234-608183.mp4" 
# video_path = "/media/ubuntu/a689a8e0-c15c-406d-816b-6c1d619b9930/new_motion_d60b_0121_motion_black.mp4" 
# video_path = "rtsp://Admin:1234@192.168.3.182/h264" # can be video or rtsp
# video_path = "rtsp://192.168.2.247:8554/1" # can be video or rtsp
SHOW_LIVE_SCREEN = False

# -------------------------------------------------------------- #


model_type = model_type_dict[model_mode]
ljob_in_path = f"/mnt/ramdisk/dpeng/{model_type}/in/"
img_in_path = f"/mnt/ramdisk/dpeng/{model_type}/in/image/"
ljob_out_path = f"/mnt/ramdisk/dpeng/{model_type}/out/"

def make_ljob(frameidx, img_path):
    # current_timestamp = "{}".format(str(time.time()).replace(".", ""))
    current_timestamp = str(int(time.time()*1000))

    tmp_ljob = template_ljob.copy()
    tmp_ljob["FrameIndex"] = frameidx
    tmp_ljob["Sn"] = frameidx
    tmp_ljob["Timestamp"] = current_timestamp
    tmp_ljob["Fn"] = img_path

    file_name = ljob_in_path + "{:08d}.ljob_".format(frameidx)

    with open(file_name, 'w') as f_out:
        ret = json.dumps(tmp_ljob)
        f_out.write(ret)

    return file_name

def write_text(img, text, position = (0, 0)):
    # text = "FONT_HERSHEY_DUPLEX"    
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = 1
    color = (0, 255, 255)
    thickness = 2
    lineType =  cv2.LINE_AA
    cv2.putText(img, text, position, font, size, color, thickness, lineType)

    return img


def clean_and_make_in_dir(folder_path):
    if os.path.isdir(folder_path):
        pass
        # print(f"[main] Delete old result folder: {folder_path}")
        # shutil.rmtree(folder_path)
    else:
        os.makedirs(folder_path, mode=0o777)
        print(f"[main] create folder: {folder_path}")


def clean_and_make_out_dir(folder_path):
    if os.path.isdir(folder_path):
        print(f"[main] Delete old result folder: {folder_path}")
        shutil.rmtree(folder_path)

    for i in range(8):
        os.makedirs(folder_path + f"{i}/", mode=0o777)
        print(f"[main] create folder: {folder_path}{i}/")

def output_job(img, img_in_path, cnt, orig_img_path=None, wnp=True):
    img_name = img_in_path + "{:08d}.jpg".format(cnt)
    if orig_img_path:
        shutil.copy(orig_img_path, img_name)
    elif wnp is True:
        img_name = img_in_path + "{:08d}.npy".format(cnt)
        np.save(img_name, img)
    else:
        cv2.imwrite(img_name, img)
        
    #cv2.imwrite(img_name, cv2.resize(img, (200, 200)))
    file_name = make_ljob(frameidx= cnt, img_path= img_name)
    os.rename(file_name, file_name[:-1])
    #os.remove(file_name[:-1])


if __name__ == '__main__':
    # clean_and_make_in_dir(ljob_in_path)
    clean_and_make_in_dir(img_in_path)
    # clean_and_make_out_dir(ljob_out_path)

    vid = cv2.VideoCapture(video_path)
    Ts = time.time()
    cnt = 0
    before_time = 0
    img = None
    while(True):
        # for i in range(10):
        #   _ = vid.read()[1]
        while(True):
            if len(os.listdir(img_in_path))>10:
                time.sleep(0.01)
            else:
                break
        # ret, img = vid.read()
        ## 720p ##
        
        ## 1080p and has people in the image ##
        orig_img_path = "../data/Kintetsu1.jpg"
        
        if img is None:
            img = cv2.imread(orig_img_path)
            # img = cv2.resize(img, (640, 386), interpolation=cv2.INTER_NEAREST)
        ret = True
        # time.sleep(0.02)
        if not ret:
            print("[ERROR] no input source!")
            time.sleep(0.1)
            continue
        img_name = str(time.time()).replace(".", "_")
        # img_name = "./rtsp_test/" + img_name + ".jpg"
        # cv2.imwrite(img_name, img)

        shape = img.shape
        # shape = (int(shape[1]/2), int(shape[0]/2))
        shape = (int(shape[1]), int(shape[0]))
# 
        # output_job(img_in_path, cnt, img)
        # output_job(img_in_path, cnt+20000)
        # output_job(img_in_path, cnt+40000)
        Process(target=output_job, args=(img, img_in_path, cnt)).start()
        break
        Process(target=output_job, args=(img, img_in_path, cnt+20000)).start()
        Process(target=output_job, args=(img, img_in_path, cnt+40000)).start()
        # Process(target=output_job, args=(img, img_in_path, cnt, orig_img_path)).start()
        
        # Process(target=output_job, args=(img, img_in_path, cnt+20000, orig_img_path)).start()
        # Process(target=output_job, args=(img, img_in_path, cnt+40000, orig_img_path)).start()
        

        cnt += 3
        time_pass = time.time()-Ts
        info_text = "Shape : {}, Time: {:.2f}, Frame count: {:08d}, fps: {:.2f}, fps_one: {:.2f}" \
                    .format(shape, time_pass, cnt, cnt/time_pass, 1/(time_pass-before_time))

        # ljob_text = f"Create ljob: {file_name}"
        # img = write_text(img, info_text, position = (20, 100))    
        # img = write_text(img, ljob_text, position = (20, 150))  
        
        # print(f"\r{info_text}, {ljob_text}", end = "")
        print(f"\r{info_text}", end = "")

        before_time = time.time()-Ts

        if SHOW_LIVE_SCREEN:
            img = cv2.resize(img, shape, interpolation=cv2.INTER_CUBIC)
            cv2.namedWindow('rtsp', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('rtsp', shape[0], shape[1])
            cv2.imshow('rtsp', img)
            cv2.waitKey(1)
        # break
        
