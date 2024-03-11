# Use the official PostgreSQL image as the base image
FROM postgres:latest

VOLUME ~/Postgre:/var/lib/postgresql/data

ENV POSTGRES_DB mydb
ENV POSTGRES_USER admin
ENV POSTGRES_PASSWORD 12345
ENV POSTGRES_HOST_AUTH_METHOD=trust

# Set environment variables
COPY .env /app/.env

# Copy the SQL initialization script into the container
COPY ./mydb_schema.sql /docker-entrypoint-initdb.d/mydb_schema.sql

# Expose the PostgreSQL port
EXPOSE 5432
CMD ["postgres"]