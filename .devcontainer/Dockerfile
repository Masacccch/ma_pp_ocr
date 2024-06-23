FROM ubuntu:24.04
# RUN
RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata  \
	&& apt-get install -y vim \
	&& apt-get install -y software-properties-common \
	&& apt-get install -y tesseract-ocr tesseract-ocr-jpn libtesseract-dev libleptonica-dev tesseract-ocr-script-jpan \
	&& apt-get install -y python3 python3-pip \
	&& apt -y install libopencv-dev \
	&& pip install pyocr --break-system-packages \
	&& pip install numpy --break-system-packages
RUN  pip install opencv-python  --break-system-packages \ 
	&& pip install tqdm --break-system-packages \
	&& apt install -y xclip \
	&& apt install -y git \
# END 
