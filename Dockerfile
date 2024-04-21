FROM python:3.10
# set work directory
WORKDIR /usr/src/app/
# copy project
COPY . /usr/src/app/
# install dependencies
RUN apt update -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt install tesseract-ocr-all -y
RUN pip install --user --upgrade pip
RUN pip install --user -r requirements.txt
RUN pip install Spire.Pdf
RUN pip install tabulate 
RUN pip install json_repair
RUN mkdir -p docs
ENV BOT_TOKEN=YOUR_TOKEN
ENV GIGA_TOKEN=YOUR_TOKEN
ENV HUGGINGFACEHUB_API_TOKEN=YOUR_TOKEN
ENV TES_PATH=""
# run app
CMD ["python", "main.py"]