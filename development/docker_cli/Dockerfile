FROM continuumio/miniconda3

RUN conda install -c conda-forge numpy pandas scipy
RUN pip install git+https://github.com/ictr/covid19-outbreak-simulator.git
ENTRYPOINT ["outbreak_simulator"]