# ══════════════════════════════════════════════════════════
# Q-School AI — Frontend Dockerfile (Multi-stage)
# Stages: base → development → build → production
# ══════════════════════════════════════════════════════════

# ─── Base stage: shared deps ──────────────────────────────
FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./

# ─── Development stage: hot-reload ────────────────────────
FROM base AS development

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ─── Build stage: production bundle ──────────────────────
FROM base AS build

RUN npm ci --ignore-scripts

COPY . .

RUN npm run build

# ─── Production stage: Nginx serving ─────────────────────
FROM nginx:1.27-alpine AS production

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# SPA routing: all paths → index.html
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /assets { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    gzip on; \
    gzip_types text/css application/javascript application/json image/svg+xml; \
    gzip_min_length 1024; \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
