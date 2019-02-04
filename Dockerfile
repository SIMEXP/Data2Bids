FROM python:3.6.7

LABEL maintainer=Loic Tetrel <loic.tetrel.pro@gmail.com>

USER jovyan

RUN pip3 install numpy \
	nibabel	\
	data2bids

COPY . /home/jovyan

CMD data2bids
