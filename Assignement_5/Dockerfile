FROM php:8.2-fpm-alpine

# Install PostgreSQL driver + nginx
RUN apk add --no-cache nginx postgresql-dev \
    && docker-php-ext-install pdo pdo_pgsql

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy app files
COPY app/ /var/www/html/
COPY static/ /var/www/static/

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Expose port 80
EXPOSE 80

# Start php-fpm + nginx
CMD sh -c "php-fpm -D && nginx -g 'daemon off;'"