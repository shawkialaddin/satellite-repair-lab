FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /lab
COPY lab.py evaluate_candidate.py /lab/
ENV SATLAB_CONTAINER=1 PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
ENTRYPOINT ["python3", "/lab/evaluate_candidate.py"]
