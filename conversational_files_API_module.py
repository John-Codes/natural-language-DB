from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from io import StringIO
import uvicorn
import os
import pandas as pd
import shutil
from typing import Dict

class ConversationalFilesAPI:
    
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

        # Mount the static files directory
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

          # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all methods
            allow_headers=["*"],  # Allow all headers
        )

    def setup_routes(self):
            @self.app.get("/", response_class=HTMLResponse)
            async def read_root(request: Request):
                with open("static/templates/index.html", "r") as f:
                    html_content = f.read()
                return HTMLResponse(content=html_content)
            @self.app.post("/txt2_csv/")
            async def txt2_csv(input_str: str):
                try:

                    csv_file = self.string_to_csv(input_str)
                    response = StreamingResponse(iter([csv_file.getvalue()]), media_type="text/csv")
                    response.headers["Content-Disposition"] = "attachment; filename=output.csv"
                    return response
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid input format: {str(e)}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail="Internal server error")
            
            @self.app.get("/get_headers_uploaded_csv_file/")
            async def get_headers_uploaded_csv_file():
                # Get the latest uploaded CSV file from the user_files directory
                user_files_dir = "user_files"
                csv_files = [f for f in os.listdir(user_files_dir) if f.endswith('.csv')]
                if not csv_files:
                    raise HTTPException(status_code=404, detail="No CSV files found")

                latest_file = max([os.path.join(user_files_dir, f) for f in csv_files], key=os.path.getctime)
                df = pd.read_csv(latest_file)
                headers = df.columns.tolist()
                return JSONResponse(content={"headers": headers})

            @self.app.post("/get_column_names")
            async def get_column_names(file: UploadFile = File(...)):
                try:
                    content = await file.read()
                    reader = csv.reader(content.decode('utf-8').splitlines())
                    header = next(reader)
                    if not header:
                        raise HTTPException(status_code=400, detail="The CSV file is empty or has no headers")
                    return {"column_names": header}
                except csv.Error as e:
                    raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
            
            @self.app.get("/get_headers_uploaded_csv_file/")
            async def get_headers_uploaded_csv_file():
                # Get the latest uploaded CSV file from the user_files directory
                user_files_dir = "user_files"
                csv_files = [f for f in os.listdir(user_files_dir) if f.endswith('.csv')]
                if not csv_files:
                    raise HTTPException(status_code=404, detail="No CSV files found")

                latest_file = max([os.path.join(user_files_dir, f) for f in csv_files], key=os.path.getctime)
                df = pd.read_csv(latest_file)
                headers = df.columns.tolist()
                return JSONResponse(content={"headers": headers})

            @self.app.post("/upload_file/")
            async def upload_file(file: UploadFile = File(...)):
            
                # Ensure the user_files directory exists
                os.makedirs("user_files", exist_ok=True)
                            # Clear the directory of any previous files
                for filename in os.listdir('user_files'):
                    file_path = os.path.join('user_files', filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Failed to delete {file_path}. Reason: {e}")

                # Check if the file is provided
                if file is None:
                    raise HTTPException(status_code=400, detail="No file uploaded")

                # Check the file type
                if file.content_type == "text/csv":
                    file_path = os.path.join("user_files", file.filename)
                    with open(file_path, "wb") as f:
                        f.write(await file.read())
                    return JSONResponse(content={"message": "CSV file uploaded successfully", "file_path": file_path})
                elif file.content_type in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                    raise HTTPException(status_code=501, detail="File type not implemented")
                else:
                    raise HTTPException(status_code=400, detail="Invalid file type. Only CSV, PDF, and Word files are allowed.")


            @self.app.post("/download_modified_csv_file/")
            async def download_modified_csv_file(selected_headers: Dict[str, bool]):
                try:
                    # Get the latest uploaded CSV file from the user_files directory
                    user_files_dir = "user_files"
                    csv_files = [f for f in os.listdir(user_files_dir) if f.endswith('.csv')]
                    if not csv_files:
                        raise HTTPException(status_code=404, detail="No CSV files found")

                    latest_file = max([os.path.join(user_files_dir, f) for f in csv_files], key=os.path.getctime)
                    df = pd.read_csv(latest_file)

                    # Filter the DataFrame based on the selected headers
                    selected_columns = [header for header, selected in selected_headers.items() if selected]
                    if not selected_columns:
                        raise HTTPException(status_code=400, detail="No columns selected")

                    filtered_df = df[selected_columns]

                    # Save the filtered DataFrame to a new CSV file
                    modified_file_path = os.path.join(user_files_dir, "modified_file.csv")
                    filtered_df.to_csv(modified_file_path, index=False)

                    return FileResponse(modified_file_path, filename="modified_file.csv")
                except Exception as e:
                    print(e)
                    raise HTTPException(status_code=500, detail=f"An error occurred while processing the file. Reason: {e}")
                
                
    def string_to_csv(self, input_string):
        try:
            lines = input_string.strip().split('\n')
            if not lines:
                raise ValueError("Empty input string provided.")
            data = [line.split(',') for line in lines]
            output = StringIO()
            writer = csv.writer(output)
            writer.writerows(data)
            output.seek(0)
            return output
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error processing CSV: {str(e)}")

# Instantiate the class and expose the app instance
api = ConversationalFilesAPI()
app = api.app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
