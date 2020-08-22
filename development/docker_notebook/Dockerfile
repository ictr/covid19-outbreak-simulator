FROM vatlab/sos-notebook

RUN conda install -c conda-forge ipykernel pandas matplotlib papermill scipy nbconvert -y
RUN conda install -c conda-forge sos-papermill -y
RUN conda install -c conda-forge r-readxl r-reshape2 r-stringr r-ggextra -y
RUN pip install covid19-outbreak-simulator

#ENTRYPOINT ["sos", "convert"]
