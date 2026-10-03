compose = '''version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - \"8000:8000\"
    environment:
      - PORT=8000
      - HISHAB_DB_PATH=/tmp/hishab.db
    restart: unless-stopped
'''
with open('docker-compose.yml', 'w', encoding='utf-8') as f:
    f.write(compose)
print('docker-compose fixed')
