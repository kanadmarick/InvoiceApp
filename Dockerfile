# Use Python 3.13 to match local dev environment and Django 5.2.7 requirements (needs >=3.10)
FROM python:3.13-slim

# Add a label to the image to show who is the maintainer
LABEL maintainer="kanadmarick@gmail.com"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
# Setting the environment variable 'PYTHONDONTWRITEBYTECODE' to 1, instructing Python not to create .pyc files for faster imports during deployment or build processes that require isolation between developers.
ENV PYTHONUNBUFFERED 1 
# With PYTHONUNBUFFERED 1, every print statement or log message appears instantly, giving you true real-time visibility into your container's behavior.
ENV PATH="/py/bin:$PATH" 
# Adding the virtual environment's bin directory to the PATH environment variable allows you to run the installed packages without needing to specify the full path, making it easier to execute commands and scripts that rely on those packages.
# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's Chromium browser and its OS-level dependencies
# Required for PDF generation (billings/pdf.py)
RUN playwright install --with-deps chromium

# Copy the rest of the application's code
COPY . /app/

# Collect static files (admin CSS/JS, DRF assets) so WhiteNoise can serve them
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
