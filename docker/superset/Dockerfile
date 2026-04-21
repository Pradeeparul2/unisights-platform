FROM apache/superset:6.0.0

USER root

RUN apt-get update && apt-get install -y build-essential

RUN pip install pydruid==0.6.6

RUN cp -r /usr/local/lib/python3.10/site-packages/pydruid* \
        /app/.venv/lib/python3.10/site-packages/

USER superset