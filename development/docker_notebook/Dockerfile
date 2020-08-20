FROM continuumio/miniconda3

RUN conda install -c conda-forge ipykernel pandas matplotlib papermill scipy nbconvert -y
RUN conda install -c conda-forge r-essentials -y
RUN conda install -c conda-forge sos sos-notebook sos-python sos-papermill -y
RUN conda install -c conda-forge r-readxl r-reshape2 r-stringr r-ggextra -y
RUN pip install covid19-outbreak-simulator

ENTRYPOINT ["sos", "convert"]