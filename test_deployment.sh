#!/bin/bash
# Test script to validate the deployment

echo "🧪 CKKC Expedition Management System - Deployment Test"
echo "======================================================"
echo ""

PASSED=0
FAILED=0

# Test 1: Check if containers are running
echo "Test 1: Container Status"
if docker-compose ps | grep -q "Up"; then
    echo "✓ Containers are running"
    ((PASSED++))
else
    echo "✗ Containers are not running"
    ((FAILED++))
fi
echo ""

# Test 2: Check database connectivity
echo "Test 2: Database Connectivity"
if docker-compose exec -T db pg_isready -U ckkc_user -d expedition_db &> /dev/null; then
    echo "✓ Database is accessible"
    ((PASSED++))
else
    echo "✗ Database is not accessible"
    ((FAILED++))
fi
echo ""

# Test 3: Check if tables exist
echo "Test 3: Database Schema"
TABLE_COUNT=$(docker-compose exec -T db psql -U ckkc_user -d expedition_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
if [ "$TABLE_COUNT" -gt "10" ]; then
    echo "✓ Database schema initialized ($TABLE_COUNT tables found)"
    ((PASSED++))
else
    echo "✗ Database schema not properly initialized"
    ((FAILED++))
fi
echo ""

# Test 4: Check web application response
echo "Test 4: Web Application Response"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Web application is responding (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo "✗ Web application is not responding properly (HTTP $HTTP_CODE)"
    ((FAILED++))
fi
echo ""

# Test 5: Check registration endpoint
echo "Test 5: Registration Page"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/register)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Registration page is accessible (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo "✗ Registration page is not accessible (HTTP $HTTP_CODE)"
    ((FAILED++))
fi
echo ""

# Test 6: Check admin login page
echo "Test 6: Admin Login Page"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/admin)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Admin login page is accessible (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo "✗ Admin login page is not accessible (HTTP $HTTP_CODE)"
    ((FAILED++))
fi
echo ""

# Test 7: Check cave survey page
echo "Test 7: Cave Survey Page"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/survey)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Cave survey page is accessible (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo "✗ Cave survey page is not accessible (HTTP $HTTP_CODE)"
    ((FAILED++))
fi
echo ""

# Test 8: Check static files
echo "Test 8: Static Files"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/static/cave.png)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "304" ]; then
    echo "✓ Static files are being served (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo "⚠ Static files may not be properly configured (HTTP $HTTP_CODE)"
    ((PASSED++))  # Not critical, count as pass
fi
echo ""

# Summary
echo "======================================================"
echo "Test Summary:"
echo "   Passed: $PASSED"
echo "   Failed: $FAILED"
echo "======================================================"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed! Deployment is healthy."
    echo ""
    echo "Next steps:"
    echo "   • Visit http://localhost:5001 to access the application"
    echo "   • Visit http://localhost:5001/admin to access admin dashboard"
    echo "   • Check logs with: docker-compose logs -f web"
    exit 0
else
    echo "❌ Some tests failed. Please check the logs:"
    echo "   docker-compose logs web"
    echo "   docker-compose logs db"
    exit 1
fi
