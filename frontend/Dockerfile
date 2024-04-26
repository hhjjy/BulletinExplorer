FROM node:18.19.1

WORKDIR /app

COPY package.json .

RUN npm install

COPY . .

CMD ["npm", "run", "build"]
# CMD ["bash", "-c", "while true; do sleep 86400; done"]