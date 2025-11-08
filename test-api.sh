#!/bin/bash
# Quick test script for PodCharts API

echo "Testing PodCharts API..."
echo ""

echo "1. Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo "2. Leaderboard (all):"
curl -s "http://localhost:8000/leaderboard" | python3 -m json.tool | head -n 20
echo ""

echo "3. Leaderboard (technology category):"
curl -s "http://localhost:8000/leaderboard?category=technology" | python3 -m json.tool | head -n 20
echo ""

echo "4. Get first podcast ID from leaderboard:"
PODCAST_ID=$(curl -s "http://localhost:8000/leaderboard" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['items'][0]['id'] if data.get('items') else '')")
echo "Podcast ID: $PODCAST_ID"
echo ""

if [ ! -z "$PODCAST_ID" ]; then
    echo "5. Podcast details:"
    curl -s "http://localhost:8000/podcast/$PODCAST_ID" | python3 -m json.tool | head -n 30
    echo ""
fi

echo "Done!"

