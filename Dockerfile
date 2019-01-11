FROM python:3.6.7

LABEL maintainer=Loic Tetrel <loic.tetrel.pro@gmail.com>

RUN apt-get update && apt-get install -y \
	numpy \
	nibabel	
COPY raw2bids.py /

CMD python raw2bids.py
