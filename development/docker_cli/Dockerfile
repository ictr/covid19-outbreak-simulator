FROM continuumio/miniconda3

RUN conda install -c conda-forge numpy pandas scipy pyyaml
RUN pip install git+https://github.com/ictr/covid19-outbreak-simulator.git
RUN mkdir /home/bcmictr
WORKDIR /home/bcmictr

ENTRYPOINT ["outbreak_simulator"]
