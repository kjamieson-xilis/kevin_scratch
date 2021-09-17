from enum import Enum

from fastapi import FastAPI

app = FastAPI()





##
# Copyright (c) 2021 - Xilis, Inc
##

import json

import cv2
import numpy as np
import torch
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from PIL import Image



from typing import List, TypedDict
from uuid import uuid4


class Point(TypedDict):
    """A single point in a given contour."""

    x: float
    y: float

class Contour(TypedDict):
    """All the data to render a contour on the frontend."""

    area: float
    id: str
    points: List[Point]


class SerializedOutput(TypedDict):
    """The output of an analytics method."""

    data: List[Contour]
    type: str

MINIMUM_AREA = 200
MAXIMUM_AREA = 8000


def extract_contour_data(contours) -> List[Contour]:
    """Converts a set of contours from cv2.findContours into something the frontend can render reliably."""
    contour_data = []

    for single_contour in contours:
        contour_area = cv2.contourArea(single_contour)
        if contour_area > MINIMUM_AREA and contour_area < MAXIMUM_AREA:
            points_in_contour = []
            for all_points in single_contour:
                for point in all_points:
                    points_in_contour.append(
                        {"x": float(point[0]), "y": float(point[1])}
                    )
            contour_data.append(
                {"area": contour_area, "id": str(uuid4()), "points": points_in_contour}
            )

    return contour_data

class Detectron2Model:
    """Productionizes the model built on Detectron2 (a facebook ML package)."""

    def __init__(self, path_to_model: str, path_to_image_local: str):
        self._configuration = get_cfg()
        self._configuration.merge_from_file(
            model_zoo.get_config_file(
                "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml"
            )
        )
        self._configuration.MODEL.WEIGHTS = path_to_model
        self._configuration.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMG = 512
        self._configuration.MODEL.ROI_HEADS.NUM_CLASSES = 1
        self._configuration.MODEL.ROI_HEADS.NMS_THRESH_TEST = 0.25
        self._configuration.MODEL.DEVICE = "cuda"

        self._predictor = DefaultPredictor(self._configuration)
        self._mask_data = []
        self._segment_image(path_to_image_local)

    def _segment_image(self, path_to_image_local: str):
        """
        Cleans up and then runs the py-torch based Detectron2 model. It extracts data only from the predicted masks
        objects from the results.
        """
        image = Image.open(path_to_image_local)
        image_as_uint8 = (
            np.array(image.getdata())
            .reshape(image.size[1], image.size[0])
            .astype(np.uint8)
        )
        gray_scale_image = cv2.cvtColor(image_as_uint8, cv2.COLOR_GRAY2BGR)
        _, margin = cv2.threshold(gray_scale_image, 20, 255, cv2.THRESH_BINARY)
        bitwise_image_and = cv2.bitwise_and(gray_scale_image, margin)
        padded_image = np.pad(
            bitwise_image_and,
            ((0, 1024), (0, 1024), (0, 0)),
            "constant",
            constant_values=0,
        )

        predictions = self._predictor.model(
            [{"image": torch.tensor(padded_image[:, :, 0])}]
        )
        all_instances = [prediction["instances"] for prediction in predictions]

        self._mask_data = []

        for instance in all_instances:
            prediction_masks_as_array = (
                instance.get_fields()["pred_masks"].cpu().numpy()
            )
            for mask in prediction_masks_as_array:
                all_contours_in_mask, _ = cv2.findContours(
                    mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                )
                self._mask_data.extend(extract_contour_data(all_contours_in_mask))

    def serialize(self) -> SerializedOutput:
        """Returns a serialized output of the results for upload to S3."""
        return json.dumps({"data": self._mask_data, "type": "detectron2"})

@app.get("/run_model")
def run_model():
    FILEPATH = "/home/kevin/git/kevin_scratch/fastapi_poc/fastapi_poc"
    #image_file = f"{FILEPATH}/Well_B2_Ch1_1um.tiff"
    image_file = f"{FILEPATH}/Well_B2_Xmm-0.012_Ymm-0.018_Ch1_1um.tiff"
    model_file = f"{FILEPATH}/wbq_organoid_model_02Sep2021.pth"
    results = Detectron2Model(model_file, image_file)
    return {"data": results._mask_data, "type": "detectron2"}



@app.get("/")
def root():
    return {"message": "Hello World"}
