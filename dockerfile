# First stage: Install dependencies
FROM python:3.13-slim AS build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev gcc && \
    pip install --upgrade pip && pip install --user --no-cache-dir -r requirements.txt

# Final stage: Smaller runtime image
FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# Install system deps needed at runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*
# Copy virtualenv/pip cache from builder
COPY --from=build /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use a non-root user for security
RUN useradd -m myuser && chown -R myuser /app
USER myuser

# Expose Gunicorn port
EXPOSE 8000

# Removed healthcheck for v1 - add back later if needed

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]



# # First stage: Install dependencies
# FROM python:3.13-slim AS build
# ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# WORKDIR /app
# COPY requirements.txt .
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev gcc && \
#     pip install --upgrade pip && pip install --user --no-cache-dir -r requirements.txt

# # Final stage: Smaller runtime image
# FROM python:3.13-slim AS runtime
# ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# WORKDIR /app
# # Install system deps needed at runtime
# RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*
# # Copy virtualenv/pip cache from builder
# COPY --from=build /root/.local /root/.local
# ENV PATH=/root/.local/bin:$PATH
# COPY . .
# COPY entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh

# # Use a non-root user for security
# RUN useradd -m myuser && chown -R myuser /app
# USER myuser

# # Expose Gunicorn port
# EXPOSE 8000

# # Healthcheck for container orchestrators
# HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
#   CMD curl -f http://localhost:8000/health/ || exit 1

# ENTRYPOINT ["/app/entrypoint.sh"]
# CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
