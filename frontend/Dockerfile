FROM node:20-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
