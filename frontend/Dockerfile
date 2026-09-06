FROM node:18-alpine

WORKDIR /app

# copy package manifests first to leverage Docker cache
COPY package.json package-lock.json* ./
RUN npm install --include=optional \
	&& npm install --no-save @rollup/rollup-linux-x64-musl

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
