# SPDX-License-Identifier: Apache-2.0
# GCR pin — Docker Hub python: and public.ecr.aws are factory exit 128.
# CPython 3.12 matches the passing local and CI test baseline.
# Digest = the multi-arch OCI index mirror.gcr.io served for 3.12-slim on
# 2026-11-06; Dependabot refreshes it (tag bumps past 3.12 are ignored there).
FROM mirror.gcr.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
WORKDIR /app
COPY szl_os ./szl_os
COPY app.py index.html szl-holo-v2.css szl-holo-v2.js ./
EXPOSE 7860
ENV PORT=7860
CMD ["python", "app.py"]
