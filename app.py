from fastapi.staticfiles import StaticFiles
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, Request
import uvicorn
import cv2
import tensorflow as tf
import hashlib
import csv
import re
from starlette.templating import Jinja2Templates
templates = Jinja2Templates(directory="finalFrontend")

app = FastAPI()
app.mount("/static", StaticFiles(directory="finalFrontend"), name="static")

model = tf.keras.models.load_model('Plantify.h5')


def evaluate_string(s):
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()-+]).{8,16}$"
    return bool(re.match(regex, s))


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


@app.post("/images/")
async def create_upload_file(request: Request,file: UploadFile = File(...)):
    """POST request with file=path of the file"""
    # image = cv2.imread(file.file)

    try:
        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        preprocessed_image = cv2.resize(image, (150, 150))
        preprocessed_image = preprocessed_image.astype("float32") / 255.0
        preprocessed_image = np.expand_dims(preprocessed_image, axis=0)

        predictions = model.predict(preprocessed_image)
        predicted_class = np.argmax(predictions)
        class_labels=["Daisy","Danelion","Rose","Sunflower","Tulip"]
        flower=class_labels[predicted_class]
        # Display the name of the plant
        # if predicted_class == 0:
        #     flower = "sunflower"
        #     return {"The uploaded image is of": "Daisy"}
        # elif predicted_class == 1:
        #     return {"The uploaded image is of": "Danelion"}
        # elif predicted_class == 2:
        #     return {"The uploaded image is of": "Rose"}
        # elif predicted_class == 3:
        #     return {"The uploaded image is of": "Sunflower"}
        # elif predicted_class == 4:
        #     return {"The uploaded image is of": "Tulip"}
        return templates.TemplateResponse("upload.html", {"request": request,"flower":flower})
    except Exception as e:

        return {"Please upload a file!"}


@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/upload")
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("homepageplantify.html", {"request": request})

@app.get("/aboutus")
async def about(request: Request):
    return templates.TemplateResponse("aboutus.html", {"request": request})

@app.get("/documentation")
async def docs(request: Request):
    return templates.TemplateResponse("documentation.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, fname: str = Form(...), lname: str = Form(...), un: str = Form(...), email_id: str = Form(...), phone_no: int = Form(...), pw: str = Form(...), repw: str = Form(...), how_know: str = Form(...)):
    if "@" not in email_id:
        return {"error": "enter valid email id"}
    if evaluate_string(pw) == False:
        return {"error": "enter a stronger password"}
    if pw != repw:
        return {"error": "passwords don't match"}
    hashed_password = hashlib.sha256(pw.encode()).hexdigest()
    with open('db.csv', "a") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([un, hashed_password, fname,
                            lname, email_id, phone_no, how_know])
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/login")
async def verify(request: Request, un: str = Form(...), pw: str = Form(...)):
    hashed_password = hashlib.sha256(pw.encode()).hexdigest()
    with open('db.csv') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row != []:
                if row[0] == un and row[1] == hashed_password:
                    print("s")
                    return templates.TemplateResponse("upload.html", {"request": request})

    return {"error": "fail"}
if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=5000, reload=True)
