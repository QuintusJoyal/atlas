# Atlas SDK runner — headless job worker for Control Center.
# npm install happens inside the image; no host node_modules required.

ARG NPM_STRICT_SSL=true

FROM node:22-alpine
ARG NPM_STRICT_SSL=true
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm config set strict-ssl "$NPM_STRICT_SSL" && npm ci
COPY . .
CMD ["npm", "run", "runner"]
