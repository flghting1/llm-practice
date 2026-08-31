FROM docker.m.daocloud.io/library/node:22-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . ./
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM docker.m.daocloud.io/library/nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
