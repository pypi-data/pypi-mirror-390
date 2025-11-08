import os
import bentoml
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

def text2imgSD(text):
    with bentoml.SyncHTTPClient(os.getenv('TEXT2IMGSD')) as client:
        result = client.txt2img(
            prompt=text,
            num_inference_steps=1,
            guidance_scale=0.0
        )
    result = Image.open(result)
    return result

def text2imgOpenAI(text):
    from openai import OpenAI
    import base64
    from io import BytesIO
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    result = client.images.generate(
                    model="gpt-image-1",
                    prompt=text)

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    img = Image.open(BytesIO(image_bytes))
    return img