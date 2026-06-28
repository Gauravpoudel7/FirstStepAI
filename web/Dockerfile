# FirstStep AI — Web (React + Vite + Tailwind)
# Multi-stage: build with node, serve with nginx.
FROM node:20-alpine AS build

WORKDIR /srv/web

COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# ---- runtime: nginx ----
FROM nginx:1.27-alpine AS runtime

# Replace default config with one that reverse-proxies /api → api:8000
# and disables buffering for SSE streams.
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets.
COPY --from=build /srv/web/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=5 \
    CMD wget -q -O /dev/null http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]