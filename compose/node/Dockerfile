# https://hub.docker.com/_/node
FROM node:lts-alpine

# Set the working directory.
WORKDIR /app

# Copy the package.json and package-lock.json files to the container.
COPY webapp/package*.json ./

# Install npm packages.
RUN npm install -g npm@9.6.0
RUN npm install
