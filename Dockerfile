# Use a base image
FROM ubuntu:latest

# Install additional packages and set environment variables
RUN apt-get update && apt-get install -y firefox wget python3 python3-pip nodejs npm && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz && \
    tar -C /usr/local/bin/ -xzvf /tmp/geckodriver.tar.gz && \
    rm /tmp/geckodriver.tar.gz

# Set an environment variable to avoid the "no-sandbox" error
ENV MOZ_HEADLESS=1

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install npm packages
RUN npm install

# Copy the rest of the application files to the container
COPY . .

# Install pip packages specific to the application
RUN pip install beautifulsoup4 selenium
RUN pip list

# Expose the port on which your Node.js server is listening
EXPOSE 3500

# Set the default command to run when the container starts
CMD ["node", "server.js"]