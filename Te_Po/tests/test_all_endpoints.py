#!/usr/bin/env python3
"""
Comprehensive test script for Tiwhanawhana FastAPI backend endpoints.
Tests all major routes and Supabase connectivity.

Usage:
    python -m tests.test_all_endpoints

Requirements:
    - httpx
    - asyncio
    - supabase (for connectivity test)
    - pillow (for test image creation)
"""

import asyncio
import os
import sys
from io import BytesIO
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import httpx
    from PIL import Image
    from supabase import create_client
    print("✅ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: pip install httpx pillow supabase")
    sys.exit(1)


class TiwhanawhanaAPITester:
    """Test suite for Tiwhanawhana FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def log_result(self, endpoint: str, success: bool, status_code: Optional[int] = None, 
                   response_data: Any = None, error: Optional[str] = None):
        """Log test result with consistent formatting."""
        status = "✅" if success else "❌"
        result = f"{status} {endpoint}"
        
        if status_code:
            result += f" (Status: {status_code})"
            
        if response_data:
            # Truncate long responses
            data_str = str(response_data)
            if len(data_str) > 100:
                data_str = data_str[:100] + "..."
            result += f" | Response: {data_str}"
            
        if error:
            result += f" | Error: {error}"
            
        print(result)
        self.results.append({
            "endpoint": endpoint,
            "success": success,
            "status_code": status_code,
            "response": response_data,
            "error": error
        })
        
    def create_test_image(self) -> BytesIO:
        """Create a simple test image for OCR testing."""
        # Create a simple white image with black text
        img = Image.new('RGB', (300, 100), color='white')
        
        # For a real test, you'd add text to the image
        # For now, just return a simple image
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
        
    async def test_root_endpoint(self, client: httpx.AsyncClient):
        """Test GET / endpoint."""
        try:
            response = await client.get("/")
            success = response.status_code == 200
            self.log_result(
                "GET /", 
                success, 
                response.status_code, 
                response.json() if success else None,
                None if success else "Unexpected status code"
            )
        except Exception as e:
            self.log_result("GET /", False, error=str(e))
            
    async def test_ocr_endpoint(self, client: httpx.AsyncClient):
        """Test POST /ocr/image endpoint."""
        try:
            test_image = self.create_test_image()
            files = {"file": ("test.png", test_image, "image/png")}
            
            response = await client.post("/ocr/image", files=files)
            success = response.status_code == 200
            
            response_data = None
            if success:
                try:
                    response_data = response.json()
                except:
                    response_data = response.text[:100]
                    
            self.log_result(
                "POST /ocr/image", 
                success, 
                response.status_code, 
                response_data,
                None if success else "OCR endpoint failed"
            )
        except Exception as e:
            self.log_result("POST /ocr/image", False, error=str(e))
            
    async def test_translate_endpoint(self, client: httpx.AsyncClient):
        """Test POST /translate endpoint."""
        try:
            payload = {
                "text": "Kia ora",
                "target_lang": "en"
            }
            
            response = await client.post("/translate", json=payload)
            success = response.status_code == 200
            
            response_data = None
            if success:
                try:
                    response_data = response.json()
                except:
                    response_data = response.text[:100]
                    
            self.log_result(
                "POST /translate", 
                success, 
                response.status_code, 
                response_data,
                None if success else "Translation endpoint failed"
            )
        except Exception as e:
            self.log_result("POST /translate", False, error=str(e))
            
    async def test_embed_endpoint(self, client: httpx.AsyncClient):
        """Test POST /embed endpoint."""
        try:
            payload = {
                "text": "This is a test embedding"
            }
            
            response = await client.post("/embed", json=payload)
            success = response.status_code == 200
            
            response_data = None
            if success:
                try:
                    data = response.json()
                    # For embeddings, just show if we got a vector
                    if isinstance(data, dict) and 'embedding' in data:
                        response_data = f"Embedding vector length: {len(data['embedding'])}"
                    else:
                        response_data = str(data)[:100]
                except:
                    response_data = response.text[:100]
                    
            self.log_result(
                "POST /embed", 
                success, 
                response.status_code, 
                response_data,
                None if success else "Embedding endpoint failed"
            )
        except Exception as e:
            self.log_result("POST /embed", False, error=str(e))
            
    async def test_memory_logs_endpoint(self, client: httpx.AsyncClient):
        """Test GET /memory/logs endpoint."""
        try:
            response = await client.get("/memory/logs")
            success = response.status_code == 200
            
            response_data = None
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response_data = f"Retrieved {len(data)} memory logs"
                    else:
                        response_data = str(data)[:100]
                except:
                    response_data = response.text[:100]
            elif response.status_code == 404:
                success = True  # Endpoint might not exist, that's OK
                response_data = "Endpoint not found (optional)"
                    
            self.log_result(
                "GET /memory/logs", 
                success, 
                response.status_code, 
                response_data,
                None if success else "Memory logs endpoint failed"
            )
        except Exception as e:
            self.log_result("GET /memory/logs", False, error=str(e))
            
    def test_supabase_connectivity(self):
        """Test Supabase client connectivity."""
        try:
            # Get environment variables
            supabase_url = os.getenv('DEN_URL')
            supabase_key = os.getenv('DEN_API_KEY')
            
            if not supabase_url or not supabase_key:
                self.log_result(
                    "Supabase Environment", 
                    False, 
                    error="Missing DEN_URL or DEN_API_KEY environment variables"
                )
                return
                
            # Test import
            try:
                supabase_client = create_client(supabase_url, supabase_key)
                self.log_result(
                    "Supabase Client Creation", 
                    True, 
                    response_data="Client created successfully"
                )
            except Exception as e:
                self.log_result(
                    "Supabase Client Creation", 
                    False, 
                    error=f"Failed to create client: {str(e)}"
                )
                return
                
            # Test basic connectivity with ti_memory table
            try:
                # Try a simple select query (limit 1 to avoid large responses)
                result = supabase_client.table('ti_memory').select('*').limit(1).execute()
                
                if result.data is not None:
                    self.log_result(
                        "Supabase Query Test", 
                        True, 
                        response_data=f"Successfully queried ti_memory table, {len(result.data)} records"
                    )
                else:
                    self.log_result(
                        "Supabase Query Test", 
                        False, 
                        error="Query returned None"
                    )
                    
            except Exception as e:
                # Try to insert a test record instead
                try:
                    test_record = {
                        "session_id": "test_session",
                        "user_input": "Test connectivity check",
                        "ai_response": "Test response",
                        "context_summary": "Connectivity test"
                    }
                    
                    insert_result = supabase_client.table('ti_memory').insert(test_record).execute()
                    
                    if insert_result.data:
                        self.log_result(
                            "Supabase Insert Test", 
                            True, 
                            response_data="Successfully inserted test record"
                        )
                        
                        # Clean up the test record
                        try:
                            supabase_client.table('ti_memory').delete().eq('session_id', 'test_session').execute()
                        except:
                            pass  # Cleanup failure is not critical
                    else:
                        self.log_result(
                            "Supabase Insert Test", 
                            False, 
                            error="Insert returned no data"
                        )
                        
                except Exception as insert_e:
                    self.log_result(
                        "Supabase Connectivity Test", 
                        False, 
                        error=f"Both select and insert failed: {str(e)}, {str(insert_e)}"
                    )
                    
        except Exception as e:
            self.log_result("Supabase Connectivity", False, error=str(e))
            
    async def run_all_tests(self):
        """Run all endpoint tests."""
        print("🚀 Starting Tiwhanawhana API Tests...")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test Supabase first (doesn't require API server)
        print("\n🔗 Testing Supabase Connectivity...")
        self.test_supabase_connectivity()
        
        # Test API endpoints
        print(f"\n🌐 Testing FastAPI Endpoints...")
        timeout = httpx.Timeout(30.0)  # 30 second timeout
        
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
                # Test each endpoint
                await self.test_root_endpoint(client)
                await self.test_ocr_endpoint(client)
                await self.test_translate_endpoint(client)
                await self.test_embed_endpoint(client)
                await self.test_memory_logs_endpoint(client)
                
        except Exception as e:
            self.log_result("API Connection", False, error=f"Could not connect to API: {str(e)}")
            
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        successful_tests = sum(1 for r in self.results if r['success'])
        total_tests = len(self.results)
        
        print(f"✅ Successful: {successful_tests}/{total_tests}")
        if successful_tests < total_tests:
            print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
            
        print("\n🔍 Failed Tests:")
        failed_tests = [r for r in self.results if not r['success']]
        if not failed_tests:
            print("   None! 🎉")
        else:
            for test in failed_tests:
                print(f"   • {test['endpoint']}: {test['error']}")
                
        return successful_tests == total_tests


async def main():
    """Main test runner."""
    # Check if API server should be running
    base_url = os.getenv('TIWHANAWHANA_API_URL', 'http://localhost:8000')
    
    tester = TiwhanawhanaAPITester(base_url)
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)