FROM node:current-buster-slim

WORKDIR /code

# Move this separately so install get's cached
COPY package.json /code/package.json

# Copy the remaining code over
COPY . /code/

# RUN npm install

# By default, use the production command
CMD npm run start-gateway localhost 8304
