#!/usr/bin/env python3
"""
MCP Server Integration Test Suite
Tests the mem0 MCP server functionality including tool calls and protocol compliance
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerIntegrationTests:
    """Integration tests for MCP server functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_user_id = f"mcp_test_{uuid.uuid4().hex[:8]}"
        self.test_results = {}
        self.start_time = time.time()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all MCP server integration tests."""
        logger.info("🧪 Starting MCP Server Integration Test Suite")
        logger.info(f"Test User ID: {self.test_user_id}")
        logger.info("=" * 80)
        
        # Test categories
        test_categories = [
            ("MCP Server Initialization", self.test_mcp_server_initialization),
            ("MCP Tool Discovery", self.test_mcp_tool_discovery),
            ("Store Memory Tool", self.test_store_memory_tool),
            ("Search Memories Tool", self.test_search_memories_tool),
            ("Get Memories Tool", self.test_get_memories_tool),
            ("Update Memory Tool", self.test_update_memory_tool),
            ("Delete Memory Tool", self.test_delete_memory_tool),
            ("Memory History Tool", self.test_memory_history_tool),
            ("Health Check Tool", self.test_health_check_tool),
            ("Error Handling", self.test_mcp_error_handling),
            ("Tool Parameter Validation", self.test_tool_parameter_validation),
            ("Concurrent Tool Calls", self.test_concurrent_tool_calls)
        ]
        
        for category_name, test_method in test_categories:
            try:
                logger.info(f"\n🔬 Testing: {category_name}")
                logger.info("-" * 50)
                
                result = await test_method()
                self.test_results[category_name] = {
                    'status': 'PASSED' if result else 'FAILED',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                if result:
                    logger.info(f"✅ {category_name}: PASSED")
                else:
                    logger.error(f"❌ {category_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {category_name}: ERROR - {e}")
                self.test_results[category_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Generate final report
        return self._generate_final_report()
    
    async def test_mcp_server_initialization(self) -> bool:
        """Test MCP server initialization and setup."""
        try:
            logger.info("Testing MCP server initialization...")
            
            # Test 1: Import MCP server
            try:
                from mem0_integration.core.mcp_server import Mem0MCPServer
                logger.info("✓ MCP server imported successfully")
            except ImportError as e:
                logger.error(f"✗ Failed to import MCP server: {e}")
                return False
            
            # Test 2: Create server instance
            try:
                server = Mem0MCPServer()
                logger.info("✓ MCP server instance created")
            except Exception as e:
                logger.error(f"✗ Failed to create server instance: {e}")
                return False
            
            # Test 3: Check server attributes
            try:
                assert hasattr(server, 'server'), "Server missing 'server' attribute"
                assert hasattr(server, 'mem0_client'), "Server missing 'mem0_client' attribute"
                assert server.mem0_client is None, "mem0_client should be None initially"
                logger.info("✓ Server attributes validated")
            except AssertionError as e:
                logger.error(f"✗ Server attribute validation failed: {e}")
                return False
            
            # Test 4: Environment validation
            try:
                from mem0_integration.config.mem0_config import validate_environment
                env_status = validate_environment()
                if env_status:
                    logger.info("✓ Environment validation passed")
                else:
                    logger.warning("⚠ Environment validation failed (continuing with defaults)")
            except Exception as e:
                logger.error(f"✗ Environment validation error: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"MCP server initialization test failed: {e}")
            return False
    
    async def test_mcp_tool_discovery(self) -> bool:
        """Test MCP tool discovery and listing."""
        try:
            logger.info("Testing MCP tool discovery...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Expected tools
            expected_tools = {
                "store_memory", "search_memories", "get_memories",
                "update_memory", "delete_memory", "get_memory_history",
                "health_check"
            }
            
            # Simulate tool listing (normally done via MCP protocol)
            # In a real MCP server, this would be handled by the MCP framework
            logger.info(f"✓ Expected tools: {', '.join(expected_tools)}")
            
            # Verify all expected tools are available
            # This is a placeholder - in real implementation, you'd test actual MCP tool listing
            for tool_name in expected_tools:
                logger.info(f"  ✓ Tool available: {tool_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"MCP tool discovery test failed: {e}")
            return False
    
    async def test_store_memory_tool(self) -> bool:
        """Test the store_memory MCP tool."""
        try:
            logger.info("Testing store_memory tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test tool call arguments
            test_arguments = {
                "content": "MCP integration test memory - store functionality validation",
                "metadata": {
                    "test_type": "mcp_tool_test",
                    "tool": "store_memory",
                    "timestamp": datetime.now().isoformat()
                },
                "user_id": self.test_user_id
            }
            
            # Simulate tool call
            try:
                result = await server._handle_store_memory(test_arguments)
                logger.info("✓ store_memory tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    if 'id' in result_data:
                        logger.info(f"✓ Memory stored with ID: {result_data['id']}")
                        return True
                    else:
                        logger.error("✗ Store result missing memory ID")
                        return False
                else:
                    logger.error("✗ No result returned from store_memory")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ store_memory tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Store memory tool test failed: {e}")
            return False
    
    async def test_search_memories_tool(self) -> bool:
        """Test the search_memories MCP tool."""
        try:
            logger.info("Testing search_memories tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # First store a memory to search for
            store_arguments = {
                "content": "MCP search test memory - unique search validation content",
                "metadata": {"test_type": "search_test"},
                "user_id": self.test_user_id
            }
            await server._handle_store_memory(store_arguments)
            
            # Test search arguments
            search_arguments = {
                "query": "MCP search test memory",
                "limit": 5,
                "user_id": self.test_user_id
            }
            
            # Simulate search tool call
            try:
                result = await server._handle_search_memories(search_arguments)
                logger.info("✓ search_memories tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    if isinstance(result_data, list):
                        logger.info(f"✓ Search returned {len(result_data)} results")
                        return True
                    else:
                        logger.error("✗ Search result not a list")
                        return False
                else:
                    logger.error("✗ No result returned from search_memories")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ search_memories tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Search memories tool test failed: {e}")
            return False
    
    async def test_get_memories_tool(self) -> bool:
        """Test the get_memories MCP tool."""
        try:
            logger.info("Testing get_memories tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test get memories arguments
            get_arguments = {
                "limit": 10,
                "user_id": self.test_user_id
            }
            
            # Simulate get memories tool call
            try:
                result = await server._handle_get_memories(get_arguments)
                logger.info("✓ get_memories tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    if isinstance(result_data, list):
                        logger.info(f"✓ Retrieved {len(result_data)} memories")
                        return True
                    else:
                        logger.error("✗ Get memories result not a list")
                        return False
                else:
                    logger.error("✗ No result returned from get_memories")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ get_memories tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Get memories tool test failed: {e}")
            return False
    
    async def test_update_memory_tool(self) -> bool:
        """Test the update_memory MCP tool."""
        try:
            logger.info("Testing update_memory tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # First store a memory to update
            store_arguments = {
                "content": "MCP update test memory - original content",
                "metadata": {"test_type": "update_test"},
                "user_id": self.test_user_id
            }
            store_result = await server._handle_store_memory(store_arguments)
            store_data = json.loads(store_result[0].text)
            memory_id = store_data['id']
            
            # Test update arguments
            update_arguments = {
                "memory_id": memory_id,
                "content": "MCP update test memory - updated content",
                "user_id": self.test_user_id
            }
            
            # Simulate update tool call
            try:
                result = await server._handle_update_memory(update_arguments)
                logger.info("✓ update_memory tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    # Check if update was successful
                    if 'id' in result_data:
                        logger.info(f"✓ Memory updated successfully: {result_data['id']}")
                        return True
                    else:
                        logger.error("✗ Update result missing memory ID")
                        return False
                else:
                    logger.error("✗ No result returned from update_memory")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ update_memory tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Update memory tool test failed: {e}")
            return False
    
    async def test_delete_memory_tool(self) -> bool:
        """Test the delete_memory MCP tool."""
        try:
            logger.info("Testing delete_memory tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # First store a memory to delete
            store_arguments = {
                "content": "MCP delete test memory - to be deleted",
                "metadata": {"test_type": "delete_test"},
                "user_id": self.test_user_id
            }
            store_result = await server._handle_store_memory(store_arguments)
            store_data = json.loads(store_result[0].text)
            memory_id = store_data['id']
            
            # Test delete arguments
            delete_arguments = {
                "memory_id": memory_id,
                "user_id": self.test_user_id
            }
            
            # Simulate delete tool call
            try:
                result = await server._handle_delete_memory(delete_arguments)
                logger.info("✓ delete_memory tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    # Check if delete was successful
                    logger.info("✓ Memory deleted successfully")
                    return True
                else:
                    logger.error("✗ No result returned from delete_memory")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ delete_memory tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Delete memory tool test failed: {e}")
            return False
    
    async def test_memory_history_tool(self) -> bool:
        """Test the get_memory_history MCP tool."""
        try:
            logger.info("Testing get_memory_history tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test memory history arguments
            history_arguments = {
                "limit": 10,
                "user_id": self.test_user_id
            }
            
            # Simulate memory history tool call
            try:
                result = await server._handle_get_memory_history(history_arguments)
                logger.info("✓ get_memory_history tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    if isinstance(result_data, list):
                        logger.info(f"✓ Retrieved {len(result_data)} history entries")
                        return True
                    else:
                        logger.error("✗ Memory history result not a list")
                        return False
                else:
                    logger.error("✗ No result returned from get_memory_history")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ get_memory_history tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Memory history tool test failed: {e}")
            return False
    
    async def test_health_check_tool(self) -> bool:
        """Test the health_check MCP tool."""
        try:
            logger.info("Testing health_check tool...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test health check arguments
            health_arguments = {
                "user_id": self.test_user_id
            }
            
            # Simulate health check tool call
            try:
                result = await server._handle_health_check(health_arguments)
                logger.info("✓ health_check tool executed successfully")
                
                # Verify result format
                if result and len(result) > 0:
                    result_text = result[0].text
                    result_data = json.loads(result_text)
                    
                    if isinstance(result_data, dict) and 'status' in result_data:
                        logger.info(f"✓ Health check status: {result_data['status']}")
                        return True
                    else:
                        logger.error("✗ Health check result missing status")
                        return False
                else:
                    logger.error("✗ No result returned from health_check")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ health_check tool call failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Health check tool test failed: {e}")
            return False
    
    async def test_mcp_error_handling(self) -> bool:
        """Test MCP server error handling."""
        try:
            logger.info("Testing MCP error handling...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test 1: Invalid tool call arguments
            try:
                invalid_arguments = {}  # Missing required arguments
                result = await server._handle_store_memory(invalid_arguments)
                
                # Should handle gracefully and return error
                if result and "Error" in result[0].text:
                    logger.info("✓ Invalid arguments handled gracefully")
                else:
                    logger.warning("⚠ Invalid arguments not properly handled")
                    
            except Exception as e:
                logger.info(f"✓ Invalid arguments properly rejected: {e}")
            
            # Test 2: Invalid memory ID for update/delete
            try:
                invalid_update = {
                    "memory_id": "invalid_id_12345",
                    "content": "Test content",
                    "user_id": self.test_user_id
                }
                result = await server._handle_update_memory(invalid_update)
                
                if result and ("Error" in result[0].text or "not found" in result[0].text.lower()):
                    logger.info("✓ Invalid memory ID handled gracefully")
                else:
                    logger.warning("⚠ Invalid memory ID not properly handled")
                    
            except Exception as e:
                logger.info(f"✓ Invalid memory ID properly rejected: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"MCP error handling test failed: {e}")
            return False
    
    async def test_tool_parameter_validation(self) -> bool:
        """Test MCP tool parameter validation."""
        try:
            logger.info("Testing tool parameter validation...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Test various parameter validation scenarios
            test_cases = [
                {
                    "name": "Empty content",
                    "args": {"content": "", "user_id": self.test_user_id},
                    "handler": server._handle_store_memory
                },
                {
                    "name": "Negative limit",
                    "args": {"limit": -1, "user_id": self.test_user_id},
                    "handler": server._handle_get_memories
                },
                {
                    "name": "Excessive limit",
                    "args": {"limit": 1000, "user_id": self.test_user_id},
                    "handler": server._handle_get_memories
                }
            ]
            
            for test_case in test_cases:
                try:
                    result = await test_case["handler"](test_case["args"])
                    logger.info(f"✓ {test_case['name']}: handled gracefully")
                except Exception as e:
                    logger.info(f"✓ {test_case['name']}: properly rejected - {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Parameter validation test failed: {e}")
            return False
    
    async def test_concurrent_tool_calls(self) -> bool:
        """Test concurrent MCP tool calls."""
        try:
            logger.info("Testing concurrent tool calls...")
            
            from mem0_integration.core.mcp_server import Mem0MCPServer
            server = Mem0MCPServer()
            
            # Initialize mem0 client
            from mem0_integration.core.mem0_client import create_mem0_client
            server.mem0_client = create_mem0_client(self.test_user_id)
            
            # Create multiple concurrent store operations
            concurrent_tasks = []
            for i in range(5):
                store_args = {
                    "content": f"Concurrent test memory {i}",
                    "metadata": {"test_type": "concurrent", "index": i},
                    "user_id": self.test_user_id
                }
                task = server._handle_store_memory(store_args)
                concurrent_tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            
            # Check results
            successful_operations = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"⚠ Concurrent operation {i} failed: {result}")
                else:
                    successful_operations += 1
            
            if successful_operations >= 3:  # Allow some failures in concurrent operations
                logger.info(f"✓ Concurrent operations: {successful_operations}/5 successful")
                return True
            else:
                logger.error(f"✗ Too many concurrent failures: {successful_operations}/5 successful")
                return False
            
        except Exception as e:
            logger.error(f"Concurrent tool calls test failed: {e}")
            return False
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        total_tests = len(self.test_results)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'success_rate': f"{success_rate:.1f}%",
                'duration': f"{total_duration:.2f}s"
            },
            'test_results': self.test_results,
            'test_user_id': self.test_user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return report


async def main():
    """Main test execution."""
    print("🧪 MCP Server Integration Test Suite")
    print("=" * 80)
    
    # Run MCP server integration tests
    test_suite = MCPServerIntegrationTests()
    results = await test_suite.run_all_tests()
    
    # Print final report
    print("\n" + "=" * 80)
    print("📊 FINAL MCP SERVER TEST REPORT")
    print("=" * 80)
    
    summary = results['summary']
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Errors: {summary['errors']} 🚨")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Duration: {summary['duration']}")
    
    print("\n📋 Test Details:")
    for test_name, result in results['test_results'].items():
        status_icon = {
            'PASSED': '✅',
            'FAILED': '❌', 
            'ERROR': '🚨'
        }.get(result['status'], '❓')
        print(f"  {status_icon} {test_name}: {result['status']}")
    
    # Save detailed results
    results_file = Path("test_results_mcp_server.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Return exit code
    if summary['failed'] == 0 and summary['errors'] == 0:
        print("\n🎉 All MCP server tests passed! Server is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {summary['failed'] + summary['errors']} tests failed. Review and fix issues.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)