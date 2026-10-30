# SPDX-License-Identifier: Apache-2.0
# GCR pin — Docker Hub python: and public.ecr.aws are factory exit 128.
# CPython 3.12 matches the passing local and CI test baseline.
FROM mirror.gcr.io/library/python:3.12-slim
WORKDIR /app
COPY szl_os ./szl_os
COPY app.py index.html ./
EXPOSE 7860
ENV PORT=7860
CMD ["python", "app.py"]
