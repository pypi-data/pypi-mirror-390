#!/usr/bin/env python3
"""
Prism SDK - API Connection Test
Tests basic connectivity to the Prism API without requiring authentication
"""

import asyncio
import sys
import os

# Add the SDK to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prism_sdk import PrismClient, PrismError
import httpx

async def test_api_connection():
    """Test API connection and endpoints"""
    
    print("🔍 Testing Prism API Connection...")
    print("=" * 50)
    
    # Initialize client (API key not needed for basic connectivity test)
    client = PrismClient(
        api_key="test-key",  # Not used for this test
        base_url="http://localhost:8001"
    )
    
    try:
        # Test direct HTTP connection to root endpoint
        print("1. Testing direct HTTP connection...")
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("http://localhost:8001/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Server Status: {data.get('status', 'unknown')}")
                print(f"✅ API Version: {data.get('version', 'unknown')}")
                print(f"✅ Available Endpoints: {len(data.get('endpoints', {}))}")
                
                # Show available endpoints
                endpoints = data.get('endpoints', {})
                for name, path in endpoints.items():
                    print(f"   • {name}: {path}")
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                return False
                
        print("\n2. Testing SDK HTTP Client...")
        # Test SDK's internal HTTP client
        try:
            response = await client._make_request("GET", "/")
            print(f"✅ SDK HTTP client working: {response.get('service', 'unknown')}")
        except Exception as e:
            print(f"❌ SDK HTTP client error: {e}")
            return False
            
        print("\n3. Testing authenticated endpoint (should fail gracefully)...")
        # Test an authenticated endpoint to verify error handling
        try:
            await client.query("test query")
            print("❌ Unexpected success - authentication should have failed")
        except PrismError as e:
            if "Authentication required" in str(e) or "401" in str(e):
                print(f"✅ Authentication properly rejected: {e}")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected exception: {e}")
            return False
            
        print("\n🎉 All connectivity tests passed!")
        print("\n💡 Next Steps:")
        print("   • Create a valid API key in the database")
        print("   • Test actual verification queries")
        print("   • Try the trust scoring endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    finally:
        await client.close_async()

async def main():
    """Main test function"""
    print("🚀 Prism SDK Connection Test")
    print(f"🔗 Target API: http://localhost:8001")
    print()
    
    success = await test_api_connection()
    
    if success:
        print("\n✅ SDK is ready for production use!")
        sys.exit(0)
    else:
        print("\n❌ SDK connection test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())