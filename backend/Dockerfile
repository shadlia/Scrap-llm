FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY . .

# Install dependencies without installing the project as a package
RUN poetry install


# Run crawl4ai setup
RUN poetry run crawl4ai-setup

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "serve"] 