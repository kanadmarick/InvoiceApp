# =============================================================
# Nginx Dockerfile — Multi-stage build
# Stage 1: Build React SPA with Node.js
# Stage 2: Serve with Nginx (reverse proxy + SPA)
# =============================================================

# ── Stage 1: Build React Frontend ─────────────────────────────
FROM node:22-alpine AS frontend-build
WORKDIR /app

# Install dependencies first (layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --production=false

# Copy source and build
COPY frontend/ .

# In production, API calls go to the same origin (Nginx proxies them)
# So VITE_API_URL should be empty (relative URLs)
ENV VITE_API_URL=
RUN npm run build

# ── Stage 2: Nginx ────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our Nginx configs (HTTP-only initially, switch to SSL after certbot)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy the React SPA build output
COPY --from=frontend-build /app/dist /usr/share/nginx/html

EXPOSE 80 443
