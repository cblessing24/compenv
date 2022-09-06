ARG BASE=python:3.8
FROM $BASE
RUN pip install pdm
WORKDIR src
COPY . .
ARG COMPENV_REF
LABEL compenv.ref=$COMPENV_REF
RUN pre-commit install --install-hooks
RUN python -m venv .venv \
    && pdm install --dev --no-lock
ENTRYPOINT ["pdm", "run"]
