FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.9.0-gpu-py38-cu111-ubuntu20.04 
COPY install-packages.sh .
RUN ./install-packages.sh
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser
COPY install-poetry.py .
RUN python3.8 ./install-poetry.py --version 1.2.0a2
ENV PATH="/home/appuser/.local/bin:$PATH"
RUN rm install-poetry.py
