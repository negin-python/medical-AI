from fastapi import FastAPI,UploadFile,File,HTTPException
import uuid
import os
import shutil


router = FastAPI()


@router.post("/uploads")
def upload_file(file:UploadFile=File(...)):
     allowed_types = [
          "image/jpeg",
          "image/jpg",
          "image/png",
          "application/pdf"
     ]
     file.file.seek(0,2)
     file_size = file.file.tell()
     file.file.seek(0)
     if file.content_type not in allowed_types:
          raise HTTPException(
               status_code=400,
               detail="File Type is not allowed"
          )
     if file_size > MAX_FILE_SIZE:
          raise HTTPException(
               status_code=400,
               detail="File is too large"
          )
     if file.content_type.startswith("image/"):
          try:
               image = image.open(file.file)
               image.verify()
          except Exception:
               raise HTTPException(
                    status_code=400,
                    detail="invalid image file"
               )

     extension = os.path.splitext(file.filename)[1]
     new_file_name = f"{uuid.uuid4()}{extension}"

     file_path = os.path.join(UPLOADS_DIR,new_file_name)

     with open(file_path) as buffer:
          shutil.copyfileobj(file.file,buffer)

     return {
          "filename":file.filename,
          "message":"File Uploads Successfully"
     }




