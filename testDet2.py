import argparse

import cv2
import numpy as np
import re
import os

from detectron2 import model_zoo
from detectron2.config import get_cfg, CfgNode
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor
from detectron2.structures import Instances
from detectron2.utils.visualizer import Visualizer, VisImage


def _get_parsed_args() -> argparse.Namespace:
    """
    Create an argument parser and parse arguments.

    :return: parsed arguments as a Namespace object
    """

    parser = argparse.ArgumentParser(description="Detectron2 demo")

    # default model is the one with the 2nd highest mask AP
    # (Average Precision) and very high speed from Detectron2 model zoo
    parser.add_argument(
        "--base_model",
        default="COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml",
        help="Base model to be used for training. This is most often "
             "appropriate link to Detectron2 model zoo."
    )

    parser.add_argument(
        "--images",
        nargs="+",
        help="A list of space separated image files that will be processed. "
             "Results will be saved next to the original images with "
             "'_processed_' appended to file name."
    )

    return parser.parse_args()


def det2run(filename):
    args: argparse.Namespace = _get_parsed_args()

    cfg: CfgNode = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(args.base_model))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(args.base_model)
    predictor: DefaultPredictor = DefaultPredictor(cfg)

    directory = './static/client/img' # Directory for taking and putting the image
    img: np.ndarray = cv2.imread(os.path.join(directory, filename))
    x, y = img.shape[0:2]
    origin_img = img
    img = cv2.resize(img, (400, 400))
    output: Instances = predictor(img)["instances"]
    store_removal_mask(output,origin_img)
    v = Visualizer(img[:, :, ::-1],
                   MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
                   scale=1.0)
    result: VisImage = v.draw_instance_predictions(output.to("cpu"))
    result_image: np.ndarray = result.get_image()[:, :, ::-1]
    result_image = cv2.resize(result_image, (y, x))
    cv2.imwrite(os.path.join(directory, filename), result_image)


def store_removal_mask(output_instance,img):
  removal_mask = np.zeros((400,400),dtype=bool)
  for i in range(output_instance.pred_classes.shape[0]):
    if output_instance.pred_classes[i] == 0:
      removal_mask = removal_mask | output_instance.pred_masks.cpu().numpy()[i]
  np.save('./static/client/mask.npy', removal_mask)
  np.save('./static/client/img.npy', img)





