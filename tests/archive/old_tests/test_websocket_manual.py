#!/usr/bin/env python
"""
Test script for Analytics Microservice v3 WebSocket API.
"""

import asyncio
import json
import websockets
import base64
from datetime import datetime

async def test_analytics():
    """Test analytics chart generation via WebSocket."""
    uri = "ws://localhost:8080/ws"
    
    print(f"🔌 Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to Analytics Microservice v3")
        
        # Wait for connection message
        connection_msg = await websocket.recv()
        print(f"📨 Connection message: {json.loads(connection_msg)['message']}")
        
        # Test 1: Simple bar chart
        print("\n📊 Test 1: Generating bar chart...")
        request = {
            "type": "analytics_request",
            "request_id": "test-001",
            "content": "Show quarterly revenue growth for 2024",
            "title": "Q1-Q4 2024 Revenue",
            "chart_type": "bar_vertical",
            "theme": "professional"
        }
        
        await websocket.send(json.dumps(request))
        print("📤 Request sent")
        
        # Receive responses (progress updates and final chart)
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data['type'] == 'progress':
                print(f"⏳ Progress: {data['stage']} - {data['progress']}% - {data.get('message', '')}")
            
            elif data['type'] == 'analytics_response':
                print(f"✅ Chart generated successfully: {data['success']}")
                if data['success']:
                    # Save the chart
                    chart_base64 = data['chart']
                    chart_bytes = base64.b64decode(chart_base64)
                    
                    filename = f"test_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    with open(filename, 'wb') as f:
                        f.write(chart_bytes)
                    
                    print(f"💾 Chart saved as: {filename}")
                    print(f"📊 Chart type: {data['metadata']['chart_type']}")
                    print(f"🎨 Theme: {data['metadata']['theme']}")
                    print(f"⏱️ Generation time: {data['metadata']['generation_time_ms']}ms")
                else:
                    print(f"❌ Error: {data.get('error', 'Unknown error')}")
                break
        
        # Test 2: Chart with user data
        print("\n📊 Test 2: Chart with user-provided data...")
        request2 = {
            "type": "analytics_request",
            "request_id": "test-002",
            "content": "Visualize sales data",
            "title": "Monthly Sales",
            "data": [
                {"label": "Jan", "value": 45000},
                {"label": "Feb", "value": 52000},
                {"label": "Mar", "value": 48000},
                {"label": "Apr", "value": 61000}
            ],
            "chart_type": "line",
            "theme": "colorful"
        }
        
        await websocket.send(json.dumps(request2))
        
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data['type'] == 'progress':
                print(f"⏳ Progress: {data['progress']}%")
            
            elif data['type'] == 'analytics_response':
                if data['success']:
                    print("✅ Chart with user data generated successfully!")
                    # Save this chart too
                    chart_base64 = data['chart']
                    chart_bytes = base64.b64decode(chart_base64)
                    
                    filename = f"test_chart_userdata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    with open(filename, 'wb') as f:
                        f.write(chart_bytes)
                    
                    print(f"💾 Chart saved as: {filename}")
                break
        
        # Test 3: Different chart types
        print("\n📊 Test 3: Testing different chart types...")
        chart_types = ["pie", "scatter", "heatmap", "histogram"]
        
        for chart_type in chart_types:
            print(f"\n🎯 Testing {chart_type} chart...")
            request = {
                "type": "analytics_request",
                "request_id": f"test-{chart_type}",
                "content": f"Generate sample data for {chart_type} visualization",
                "chart_type": chart_type,
                "theme": "default"
            }
            
            await websocket.send(json.dumps(request))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data['type'] == 'analytics_response':
                    if data['success']:
                        print(f"  ✅ {chart_type} chart generated successfully")
                    else:
                        print(f"  ❌ {chart_type} failed: {data.get('error')}")
                    break
        
        print("\n🎉 All tests completed!")

async def test_concurrent_connections():
    """Test multiple concurrent WebSocket connections."""
    print("\n🔄 Testing concurrent connections...")
    
    async def create_chart(connection_id: int):
        uri = "ws://localhost:8080/ws"
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            await websocket.recv()
            
            request = {
                "type": "analytics_request",
                "request_id": f"concurrent-{connection_id}",
                "content": f"Chart for connection {connection_id}",
                "chart_type": "bar_vertical"
            }
            
            await websocket.send(json.dumps(request))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data['type'] == 'analytics_response':
                    return data['success']
    
    # Create 5 concurrent connections
    tasks = [create_chart(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"✅ Concurrent test: {success_count}/5 successful")

async def interactive_test():
    """Interactive test mode."""
    uri = "ws://localhost:8080/ws"
    
    print("\n🎮 Interactive Test Mode")
    print("Enter chart requests or 'quit' to exit\n")
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()
        print("Connected! Try commands like:")
        print("  - Show monthly sales trends")
        print("  - Create a pie chart of market share")
        print("  - Visualize temperature data over time")
        print()
        
        while True:
            content = input("📝 Enter request (or 'quit'): ")
            if content.lower() == 'quit':
                break
            
            chart_type = input("📊 Chart type (bar_vertical/line/pie/scatter): ") or "bar_vertical"
            theme = input("🎨 Theme (default/dark/professional/colorful/minimal): ") or "default"
            
            request = {
                "type": "analytics_request",
                "request_id": f"interactive-{datetime.now().timestamp()}",
                "content": content,
                "chart_type": chart_type,
                "theme": theme
            }
            
            await websocket.send(json.dumps(request))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data['type'] == 'progress':
                    print(f"  ⏳ {data['progress']}% - {data.get('message', '')}")
                
                elif data['type'] == 'analytics_response':
                    if data['success']:
                        print("  ✅ Chart generated successfully!")
                        save = input("  💾 Save chart? (y/n): ")
                        if save.lower() == 'y':
                            filename = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            chart_bytes = base64.b64decode(data['chart'])
                            with open(filename, 'wb') as f:
                                f.write(chart_bytes)
                            print(f"  💾 Saved as: {filename}")
                    else:
                        print(f"  ❌ Error: {data.get('error')}")
                    break
            print()

async def main():
    """Main test runner."""
    print("=" * 60)
    print("🧪 Analytics Microservice v3 - Test Suite")
    print("=" * 60)
    
    try:
        # Run basic tests
        await test_analytics()
        
        # Test concurrent connections
        await test_concurrent_connections()
        
        # Optional: Run interactive mode
        interactive = input("\n🎮 Run interactive test mode? (y/n): ")
        if interactive.lower() == 'y':
            await interactive_test()
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure the Analytics Microservice is running on port 8080")

if __name__ == "__main__":
    asyncio.run(main())