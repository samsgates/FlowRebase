FROM node:22-alpine AS deps
WORKDIR /repo
COPY packages/uam-ts ./packages/uam-ts
COPY frontend/package.json ./frontend/package.json
WORKDIR /repo/frontend
RUN npm install

FROM node:22-alpine AS build
WORKDIR /repo
COPY --from=deps /repo/frontend/node_modules ./frontend/node_modules
COPY packages/uam-ts ./packages/uam-ts
COPY frontend ./frontend
WORKDIR /repo/frontend
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=build /repo/frontend/.next/standalone ./
COPY --from=build /repo/frontend/.next/static ./frontend/.next/static
COPY --from=build /repo/frontend/public ./frontend/public
EXPOSE 3000
CMD ["node", "frontend/server.js"]
