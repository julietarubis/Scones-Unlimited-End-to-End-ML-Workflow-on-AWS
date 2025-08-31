import json, base64, boto3

s3 = boto3.client("s3")

def serialize_image_handler(event, context):
    """
    Input:
      {"image_data":"", "s3_bucket":"<bucket>", "s3_key":"test/xxx.png", "inferences":[]}
    Output (body):
      {"image_data":"<b64>", "s3_bucket":"..","s3_key":"..","inferences":[]}
    """
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
