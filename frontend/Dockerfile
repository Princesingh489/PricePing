# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Optional build argument to specify API URL at build time
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Install dependencies using clean install
COPY package*.json ./
RUN npm ci

# Copy source code and build production assets
COPY . .
RUN npm run build

# Stage 2: Serve the production build with Nginx
FROM nginx:alpine

# Copy built static files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Health check to ensure Nginx is actively serving the app
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
