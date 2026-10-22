# ── Stage 1: Build Vue 3 Frontend ──
FROM node:20-alpine AS build-stage

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy frontend source code and build production bundle
COPY . .
RUN npm run build

# ── Stage 2: Serve with Production Nginx ──
FROM nginx:alpine AS production-stage

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
