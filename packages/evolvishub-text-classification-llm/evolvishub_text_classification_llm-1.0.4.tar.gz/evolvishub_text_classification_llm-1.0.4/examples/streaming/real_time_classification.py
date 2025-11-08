#!/usr/bin/env python3
"""
Real-Time Streaming Classification Example

This example demonstrates real-time streaming classification capabilities including:
- WebSocket server for real-time client connections
- Streaming classification with progress updates
- Multiple concurrent streams
- Real-time metrics and monitoring
- Client-server communication patterns
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
import websockets
from websockets.server import WebSocketServerProtocol

from evolvishub_text_classification_llm import ClassificationEngine
from evolvishub_text_classification_llm.streaming import (
    StreamingClassificationEngine,
    StreamingRequest,
    StreamingResponse
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealTimeClassificationServer:
    """
    Real-time classification server with WebSocket support.
    
    Provides:
    - WebSocket endpoints for real-time classification
    - Multiple concurrent client support
    - Progress tracking and metrics
    - Error handling and recovery
    """
    
    def __init__(self, classification_engine: ClassificationEngine, port: int = 8765):
        """Initialize the real-time server."""
        self.classification_engine = classification_engine
        self.port = port
        self.streaming_engine = StreamingClassificationEngine(
            classification_engine=classification_engine,
            max_concurrent_streams=20,
            enable_metrics=True
        )
        
        # Connected clients
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.client_streams: Dict[str, List[str]] = {}
        
        # Server metrics
        self.server_start_time = time.time()
        self.total_connections = 0
        self.total_messages = 0
    
    async def register_client(self, websocket: WebSocketServerProtocol, client_id: str):
        """Register a new client connection."""
        self.clients[client_id] = websocket
        self.client_streams[client_id] = []
        self.total_connections += 1
        
        logger.info(f"Client {client_id} connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "client_id": client_id,
            "server_info": {
                "max_concurrent_streams": self.streaming_engine.max_concurrent_streams,
                "supported_categories": ["positive", "negative", "neutral", "mixed"],
                "server_uptime": time.time() - self.server_start_time
            }
        }
        await websocket.send(json.dumps(welcome_msg))
    
    async def unregister_client(self, client_id: str):
        """Unregister a client connection."""
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.client_streams:
            del self.client_streams[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total clients: {len(self.clients)}")
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, client_id: str, message: str):
        """Handle incoming client message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "classify":
                await self.handle_classification_request(websocket, client_id, data)
            elif message_type == "get_metrics":
                await self.handle_metrics_request(websocket, client_id)
            elif message_type == "ping":
                await self.handle_ping(websocket, client_id)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
        except Exception as e:
            await self.send_error(websocket, f"Message handling error: {e}")
    
    async def handle_classification_request(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict[str, Any]):
        """Handle classification request from client."""
        try:
            # Create streaming request
            request = StreamingRequest(
                text=data["text"],
                categories=data.get("categories", ["positive", "negative", "neutral", "mixed"]),
                metadata=data.get("metadata"),
                stream_id=f"{client_id}_{int(time.time() * 1000)}"
            )
            
            # Track stream for client
            self.client_streams[client_id].append(request.stream_id)
            
            # Send acknowledgment
            ack_msg = {
                "type": "classification_started",
                "request_id": str(request.id),
                "stream_id": request.stream_id,
                "text_length": len(request.text)
            }
            await websocket.send(json.dumps(ack_msg))
            
            # Stream classification results
            async for response in self.streaming_engine.stream_classify(request):
                # Convert response to JSON
                response_msg = {
                    "type": "classification_response",
                    "request_id": str(response.request_id),
                    "stream_id": response.stream_id,
                    "chunk_type": response.chunk_type,
                    "content": response.content,
                    "classification": response.classification,
                    "progress": response.progress,
                    "error": response.error,
                    "timestamp": response.timestamp.isoformat()
                }
                
                await websocket.send(json.dumps(response_msg))
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            # Remove stream from tracking
            if request.stream_id in self.client_streams[client_id]:
                self.client_streams[client_id].remove(request.stream_id)
            
            self.total_messages += 1
        
        except Exception as e:
            await self.send_error(websocket, f"Classification error: {e}")
    
    async def handle_metrics_request(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle metrics request from client."""
        try:
            streaming_metrics = self.streaming_engine.get_metrics()
            
            metrics_msg = {
                "type": "metrics",
                "server_metrics": {
                    "total_connections": self.total_connections,
                    "active_clients": len(self.clients),
                    "total_messages": self.total_messages,
                    "server_uptime": time.time() - self.server_start_time
                },
                "streaming_metrics": {
                    "total_requests": streaming_metrics.total_requests,
                    "active_streams": streaming_metrics.active_streams,
                    "total_responses": streaming_metrics.total_responses,
                    "total_errors": streaming_metrics.total_errors,
                    "average_response_time_ms": streaming_metrics.average_response_time_ms,
                    "throughput_per_second": streaming_metrics.throughput_per_second
                },
                "client_info": {
                    "client_id": client_id,
                    "active_streams": len(self.client_streams.get(client_id, []))
                }
            }
            
            await websocket.send(json.dumps(metrics_msg))
        
        except Exception as e:
            await self.send_error(websocket, f"Metrics error: {e}")
    
    async def handle_ping(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle ping request from client."""
        pong_msg = {
            "type": "pong",
            "timestamp": time.time(),
            "client_id": client_id
        }
        await websocket.send(json.dumps(pong_msg))
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to client."""
        error_msg = {
            "type": "error",
            "error": error_message,
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(error_msg))
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle individual client connection."""
        client_id = f"client_{int(time.time() * 1000)}_{id(websocket)}"
        
        try:
            await self.register_client(websocket, client_id)
            
            async for message in websocket:
                await self.handle_client_message(websocket, client_id, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            await self.unregister_client(client_id)
    
    async def start_server(self):
        """Start the WebSocket server."""
        logger.info(f"Starting real-time classification server on port {self.port}")
        
        # Initialize classification engine
        await self.classification_engine.initialize()
        
        # Start WebSocket server
        server = await websockets.serve(
            self.handle_client,
            "localhost",
            self.port,
            ping_interval=30,
            ping_timeout=10,
            max_size=1024*1024  # 1MB max message size
        )
        
        logger.info(f"✅ Server started on ws://localhost:{self.port}")
        logger.info("Ready to accept client connections...")
        
        return server


async def demo_real_time_server():
    """Demonstrate the real-time classification server."""
    print("\n🌐 Real-Time Classification Server Demo")
    print("=" * 50)
    
    # Create classification engine (using a mock provider for demo)
    engine = ClassificationEngine.create_simple(
        provider_type="openai",  # Replace with your preferred provider
        model="gpt-3.5-turbo",
        api_key="demo-key",  # Replace with actual API key
        categories=["positive", "negative", "neutral", "mixed"]
    )
    
    # Create server
    server = RealTimeClassificationServer(engine, port=8765)
    
    try:
        # Start server
        websocket_server = await server.start_server()
        
        print("🚀 Server is running!")
        print("📱 Connect clients using WebSocket to: ws://localhost:8765")
        print("\n📋 Supported message types:")
        print("• classify: {'type': 'classify', 'text': 'your text', 'categories': [...]}")
        print("• get_metrics: {'type': 'get_metrics'}")
        print("• ping: {'type': 'ping'}")
        
        print("\n⏹️ Press Ctrl+C to stop the server")
        
        # Keep server running
        await websocket_server.wait_closed()
    
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await engine.cleanup()


async def demo_websocket_client():
    """Demonstrate a WebSocket client for testing."""
    print("\n📱 WebSocket Client Demo")
    print("=" * 50)
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Welcome: {welcome_data}")
            
            # Test classification requests
            test_texts = [
                "I love this new feature! It's amazing!",
                "This is terrible and doesn't work at all.",
                "The product is okay, nothing special.",
                "Great quality but expensive. Mixed feelings."
            ]
            
            for i, text in enumerate(test_texts, 1):
                print(f"\n📝 Sending classification request {i}: {text[:50]}...")
                
                # Send classification request
                request = {
                    "type": "classify",
                    "text": text,
                    "categories": ["positive", "negative", "neutral", "mixed"]
                }
                await websocket.send(json.dumps(request))
                
                # Receive streaming responses
                while True:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if response_data["type"] == "classification_response":
                        chunk_type = response_data["chunk_type"]
                        
                        if chunk_type == "progress":
                            progress = response_data.get("progress", 0)
                            content = response_data.get("content", "")
                            print(f"   📊 Progress: {progress:.1%} - {content}")
                        
                        elif chunk_type == "classification":
                            classification = response_data.get("classification")
                            if classification:
                                print(f"   ✅ Result: {classification}")
                                break
                        
                        elif chunk_type == "complete":
                            print(f"   🎉 Completed")
                            break
                        
                        elif chunk_type == "error":
                            print(f"   ❌ Error: {response_data.get('error')}")
                            break
                
                # Small delay between requests
                await asyncio.sleep(1)
            
            # Get metrics
            print(f"\n📊 Requesting server metrics...")
            await websocket.send(json.dumps({"type": "get_metrics"}))
            
            metrics_response = await websocket.recv()
            metrics_data = json.loads(metrics_response)
            
            if metrics_data["type"] == "metrics":
                print(f"   Server metrics: {metrics_data['server_metrics']}")
                print(f"   Streaming metrics: {metrics_data['streaming_metrics']}")
    
    except Exception as e:
        print(f"❌ Client error: {e}")


async def demo_concurrent_clients():
    """Demonstrate multiple concurrent clients."""
    print("\n👥 Concurrent Clients Demo")
    print("=" * 50)
    
    async def client_session(client_id: int, num_requests: int = 3):
        """Simulate a client session."""
        uri = "ws://localhost:8765"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"🔗 Client {client_id} connected")
                
                # Wait for welcome
                await websocket.recv()
                
                # Send multiple requests
                for i in range(num_requests):
                    request = {
                        "type": "classify",
                        "text": f"Client {client_id} test message {i+1}: This is a sample text for classification.",
                        "categories": ["positive", "negative", "neutral"]
                    }
                    await websocket.send(json.dumps(request))
                    
                    # Wait for completion
                    while True:
                        response = await websocket.recv()
                        response_data = json.loads(response)
                        
                        if (response_data["type"] == "classification_response" and 
                            response_data["chunk_type"] in ["complete", "error"]):
                            break
                    
                    await asyncio.sleep(0.5)
                
                print(f"✅ Client {client_id} completed all requests")
        
        except Exception as e:
            print(f"❌ Client {client_id} error: {e}")
    
    # Create multiple concurrent clients
    num_clients = 5
    tasks = [client_session(i) for i in range(1, num_clients + 1)]
    
    print(f"🚀 Starting {num_clients} concurrent clients...")
    await asyncio.gather(*tasks)
    print(f"🎉 All {num_clients} clients completed!")


async def main():
    """Run streaming examples."""
    print("🌊 Real-Time Streaming Classification Examples")
    print("=" * 60)
    
    print("Choose an example to run:")
    print("1. Start real-time server")
    print("2. Test WebSocket client (requires server running)")
    print("3. Test concurrent clients (requires server running)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await demo_real_time_server()
    elif choice == "2":
        await demo_websocket_client()
    elif choice == "3":
        await demo_concurrent_clients()
    else:
        print("Invalid choice. Running server demo...")
        await demo_real_time_server()


if __name__ == "__main__":
    asyncio.run(main())
