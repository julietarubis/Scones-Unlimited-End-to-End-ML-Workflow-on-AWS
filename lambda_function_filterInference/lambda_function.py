import json, base64, boto3
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor

s3 = boto3.client("s3")

def serialize_image_handler(event, context):
  
    bucket = event["s3_bucket"]
    key = event["s3_key"]

    s3.download_file(bucket, key, "/tmp/image.png")
    with open("/tmp/image.png", "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "statusCode": 200,
        "body": {
            "image_data": image_b64,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

ENDPOINT_NAME = "image-classification-2025-08-29-05-07-52-508"

def classify_image_handler(event, context):
    """
    Input: body from serialize_image_handler
    Output: same event with inferences array added
    """
    image = base64.b64decode(event["image_data"])
    predictor = Predictor(endpoint_name=ENDPOINT_NAME)
    predictor.serializer = IdentitySerializer("image/png")

    result = predictor.predict(image)  # bytes -> b"[p_bicycle, p_motorcycle]"
    event["inferences"] = result.decode("utf-8")
    return {"statusCode": 200, "body": json.dumps(event)}

THRESHOLD = 0.93

def threshold_filter_handler(event, context):
    """
    Fail loudly if max(inferences) < THRESHOLD
    """
    inferences = event["inferences"]
    if isinstance(inferences, str):
        inferences = json.loads(inferences)

    if max(inferences) >= THRESHOLD:
        return {"statusCode": 200, "body": json.dumps(event)}
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")
