# Fetch paginated list of users from internal API
curl -s -X GET "https://api.internal.company.com/v2/users?page=1&limit=50" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Accept: application/json" | jq '.users[]'

# Upload a file to object storage
curl -X PUT "https://storage.example.com/bucket/myfile.csv" \
  -H "Content-Type: text/csv" \
  --data-binary @/tmp/report.csv \
  --retry 3

# Health check endpoint
curl -f -o /dev/null -w "%{http_code}" https://api.example.com/health
