# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the script and other necessary files
COPY bridge.py /app/
COPY utils.py /app/
COPY exporters.py /app/
COPY requirements.txt /app/
COPY .env /app/  
# Assuming your environment variables are stored in .env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the script when the container launches
CMD ["python3", "bridge.py"]
