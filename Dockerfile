# CPU-only image for the knotlab CLI (invariants + benchmarks).
FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml README.md requirements.txt ./
COPY knotlab ./knotlab
COPY invariants ./invariants
COPY topology ./topology
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir --no-deps .
RUN useradd -m knot
USER knot
ENTRYPOINT ["knotlab"]
CMD ["invariants", "figure_eight"]
