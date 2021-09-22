FROM 607182506347.dkr.ecr.us-east-1.amazonaws.com/model_server:pytorch-1.9.0-py38-ubuntu20.04_1
COPY pyproject.toml .
COPY Docker.poetry.lock ./poetry.lock
RUN poetry config virtualenvs.options.system-site-packages true --local
RUN poetry install
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'
COPY --chown=appuser:appuser fastapi_poc .
