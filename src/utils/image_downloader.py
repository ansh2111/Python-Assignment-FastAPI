import requests

def save_image_local(file_path:str, image_url: str):
    img_data = b""
    if image_url != "":
        img_data = requests.get(image_url).content
    with open(file_path, 'wb') as handler:
        handler.write(img_data)
        handler.close()