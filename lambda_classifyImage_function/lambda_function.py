# lambda_function.py  (classifyImage)
import os, json, base64, boto3

ENDPOINT_NAME = os.environ["ENDPOINT_NAME"]  # must match your endpoint exactly
rt = boto3.client("sagemaker-runtime")

def _normalize_event(evt):
    """
    Support:
      evt = {"image_data": "...", ...}
      evt = {"body": {...}}
      evt = {"body": "<json-string>"}
    """
    if "body" in evt:
        body = evt["body"]
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception:
                pass
        if isinstance(body, dict):
            # Merge nested body into top-level for convenience
            merged = dict(evt)
            merged.update(body)
            return merged
    return evt

def _clean_b64(b64: str) -> str:
   
    if isinstance(b64, bytes):
        b64 = b64.decode("utf-8", "ignore")

    if "base64," in b64[:100]:
        b64 = b64.split("base64,", 1)[1]
   
    b64 = "".join(b64.split())
   
    missing = (-len(b64)) % 4
    if missing:
        b64 += "=" * missing
    return b64

def classify_image_handler(event, context):
    
    event = _normalize_event(event)

  
    if "image_data" not in event or not event["image_data"]:
        raise ValueError("image_data is empty or missing in event; "
                         "run serializeImageData first or include full base64")
    b64 = _clean_b64(event["image_data"])

   
    img_bytes = base64.b64decode(b64, validate=False)

    
    print("Bytes length:", len(img_bytes))
    print("First 8 bytes (hex):", img_bytes[:8].hex())  

    
    resp = rt.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/x-image",
        Body=img_bytes,
    )

   
    result = resp["Body"].read().decode("utf-8")
    event["inferences"] = result
    return {"statusCode": 200, "body": json.dumps(event)}
