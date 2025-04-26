# 1. Use an official Node image to build the frontend
FROM node:18 AS builder

# 2. Set the working directory
WORKDIR /frontend

# 3. Copy package.json and package-lock.json
COPY package*.json ./

# 4. Install dependencies
RUN npm install

# 5. Copy rest of the code
COPY . .

# 6. Build the React app(this creates statuc files in /build)
RUN npm run build

# 7. Use a lightweight nginx image to serve the built app
FROM nginx:stable-alpine

# 8. Copy build ouput to nginx html directory
COPY --from=builder /frontend/build /usr/share/nginx/html

# 9. Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 10. Expose port 80
EXPOSE 80

# 11. Start nginx
CMD ["nginx", "-g", "daemon off;"]