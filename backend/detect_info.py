import torch, detectron2

# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog, DatasetCatalog


im = cv2.imread("4.jpg")
cv2.imshow("image", im)
cv2.waitKey(0)

# Inference with a panoptic segmentation model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
cfg.MODEL.DEVICE = 'cpu'
predictor = DefaultPredictor(cfg)
panoptic_seg, segments_info = predictor(im)["panoptic_seg"]

metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

wall_index = -1
for idx, item in enumerate(metadata.stuff_classes):
    if item == "wall":
        wall_index = idx
        break

if wall_index != -1:
    # Get the segment ID of the 'wall' class
    wall_segment_id = None
    for segment_info in segments_info:
        if segment_info["category_id"] == wall_index:
            wall_segment_id = segment_info["id"]
            break

    if wall_segment_id is not None:
        # Get the binary mask of the wall segment
        wall_mask = (panoptic_seg == wall_segment_id).numpy()

        # Modify the color of the wall pixels
        wall_color = [0, 0, 255]  # Red color for wall
        im[wall_mask] = wall_color

        # Save the modified image to a file or display it using cv2.imshow()
        cv2.imwrite("modified_image.jpg", im)
    else:
        print("Segment ID for 'wall' not found in panoptic segmentation output")
else:
    print("Label 'wall' not found in stuff_classes")
