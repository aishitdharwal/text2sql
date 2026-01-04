#!/bin/bash

# Start both backend and frontend servers

echo "================================"
echo "Text2SQL - Starting All Services"
echo "================================"
echo ""

# Check if we're in the phase_1 directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the phase_1 directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start Backend
echo "Starting Backend API on port 8080..."
cd backend
chmod +x run.sh
./run.sh &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start Frontend
echo "Starting Frontend on port 3000..."
cd frontend
chmod +x run.sh
./run.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================"
echo "Services Started!"
echo "================================"
echo "Backend API: http://localhost:8080"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
