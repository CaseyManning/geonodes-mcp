from google.genai import types
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def evaluate_prompt(expected_output_description: str):
    return f"""You are a 3D agent working with blender geometry nodes. Attached is the output of a specific node in the graph. We expect the output of this node to look like the following: {expected_output_description}.

    Please describe in detail whether or not the image matches the description, and if not, what specific aspects are different.
    """

def describe_prompt():
    return "You are a 3D agent working with blender geometry nodes. Attached is the output of a specific node in the graph. Please describe in detail what the visible geometry looks like. Only discuss the geometry, not the environment, lighting, or shading."

def get_response(image_bytes: bytes, prompt: str):
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/png',
        ),
        prompt
        ]   
    )
    return response.text

def evaluate_image(img_path: str, expected_output_description: str):
    print("Evaluating image: ", img_path)
    with open(img_path, 'rb') as f:
        image_bytes = f.read()

    print("read image bytes")

    response = get_response(image_bytes, evaluate_prompt(expected_output_description))

    print("got response")

    return response

def describe_image(img_path: str):
    with open(img_path, 'rb') as f:
        image_bytes = f.read()

    response = get_response(image_bytes, describe_prompt())
    return response

if __name__ == "__main__":
    expected_output_description = "a smooth sphere"

    with open('viewport_render.png', 'rb') as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/png',
        ),
        evaluate_prompt(expected_output_description)
        ]   
    )

    print(response.text)