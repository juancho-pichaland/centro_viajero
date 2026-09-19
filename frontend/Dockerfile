FROM node:20-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY package.json package-lock.json* ./
RUN npm install --include=optional --no-fund --no-audit \
    && npm install --no-save --no-fund --no-audit @rollup/rollup-linux-x64-musl

COPY . .
RUN chown -R app:app /app

USER app

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
