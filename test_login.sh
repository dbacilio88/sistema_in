#!/bin/bash
# Test login with username
echo "====================================="
echo "Testing login with username: admin"
echo "Password: admin123"
echo "====================================="
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -m json.tool

echo -e "\n\n====================================="
echo "Testing login with email: admin@traffic.local"
echo "Password: admin123"
echo "====================================="
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@traffic.local","password":"admin123"}' \
  | python3 -m json.tool


