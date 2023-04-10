from flask import Flask, request, send_file, send_from_directory
import detectron2
from detectron2.utils.logger import setup_logger

setup_logger()
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import Visualizer
from detectron2 import model_zoo
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)


def generate_segmentation(im):
    cfg = get_cfg()
    cfg.merge_from_file(
        model_zoo.get_config_file(
            "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"
        )
    )
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
        "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"
    )
    predictor = DefaultPredictor(cfg)
    panoptic_seg, segments_info = predictor(im)["panoptic_seg"]
    v = Visualizer(
        im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2
    )
    out = v.draw_panoptic_seg_predictions(panoptic_seg.to("cpu"), segments_info)
    return out.get_image()[:, :, ::-1]


@app.route("/segment", methods=["POST"])
def segment_image():
    img = Image.open(request.files["image"])
    img_np = np.array(img)
    result = generate_segmentation(img_np)
    out_img = Image.fromarray(result.astype("uint8"))
    output_filename = "output.png"
    out_img.save(output_filename)

    return send_from_directory(
        os.getcwd(),
        output_filename,
        as_attachment=True,
        attachment_filename=output_filename,
    )


if __name__ == "__main__":
    app.run(debug=True)
