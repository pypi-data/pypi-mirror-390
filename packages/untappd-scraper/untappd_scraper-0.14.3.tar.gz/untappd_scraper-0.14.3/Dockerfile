FROM warbin/poetry:390

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --only main,test