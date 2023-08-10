# Use a base image
FROM archlinux:latest

# Update package repositories and install required packages
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm firefox geckodriver python nodejs npm && \
    rm -rf /var/cache/pacman/pkg/*

# Set an environment variable to avoid the "no-sandbox" error
ENV MOZ_HEADLESS=1

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install npm packages
RUN npm install

# Create a Python virtual environment
RUN python -m venv venv

# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Install pip packages specific to the application
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip list

# Copy the rest of the application files to the container
COPY . .

# Expose the port on which your Node.js server is listening
EXPOSE 3500

# Set the default command to run when the container starts
CMD ["node", "server.js"]