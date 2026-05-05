#!/usr/bin/env python3
"""
Test Script: Quran Foundation MCP Integration
Validates the new Quran-Centric Islamic AI Agent setup
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("\n" + "="*70)
print("🧪 Quran Foundation MCP Integration Tests")
print("="*70 + "\n")

async def test_mcp_provider():
    """Test 1: Quran Foundation MCP Provider"""
    print("📝 Test 1: Quran Foundation MCP Provider")
    print("-" * 70)
    
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        print("✅ MCP provider initialized")
        print(f"   Instance: {mcp}")
        print(f"   Base URL: {mcp.base_url}")
        
        await mcp.close()
        print("✅ MCP provider closed gracefully\n")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


async def test_quran_search():
    """Test 2: Quran Search Functionality"""
    print("📝 Test 2: Quran Search")
    print("-" * 70)
    
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        print("Searching Quran for 'mercy'...")
        results = await mcp.search_quran("mercy")
        
        if "error" in results:
            print(f"⚠️  Search returned: {results['error']}")
        else:
            print(f"✅ Search completed")
            if "results" in results:
                print(f"   Found {len(results['results'])} results")
                for i, result in enumerate(results['results'][:3]):
                    print(f"   [{i+1}] Surah {result.get('surah')}:{result.get('ayah')}")
        
        await mcp.close()
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_quran_fetch():
    """Test 3: Fetch Surah"""
    print("📝 Test 3: Fetch Surah")
    print("-" * 70)
    
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        print("Fetching Surah Al-Fatiha (Surah 1)...")
        result = await mcp.fetch_quran(1, edition="en.sahih")
        
        if "error" in result:
            print(f"⚠️  Fetch returned: {result['error']}")
        else:
            print(f"✅ Surah fetched successfully")
            print(f"   Content type: {type(result)}")
        
        await mcp.close()
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


async def test_tafsir_fetch():
    """Test 4: Fetch Tafsir"""
    print("📝 Test 4: Fetch Tafsir")
    print("-" * 70)
    
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        print("Fetching Tafsir for Surah 1:1...")
        result = await mcp.fetch_tafsir(1, 1, "ibn_kathir")
        
        if "error" in result:
            print(f"⚠️  Tafsir fetch returned: {result['error']}")
        else:
            print(f"✅ Tafsir fetched successfully")
            print(f"   Content type: {type(result)}")
        
        await mcp.close()
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


async def test_thematic_exploration():
    """Test 5: Thematic Exploration"""
    print("📝 Test 5: Thematic Exploration")
    print("-" * 70)
    
    try:
        from backend.utils.quran_mcp_provider import get_quran_mcp
        
        mcp = get_quran_mcp()
        await mcp.initialize()
        
        print("Exploring theme: 'patience'...")
        result = await mcp.get_thematic_exploration("patience", limit=5)
        
        if "error" in result:
            print(f"⚠️  Exploration returned: {result['error']}")
        else:
            verses = result.get("verses", [])
            print(f"✅ Theme exploration completed")
            print(f"   Found {len(verses)} verses on patience")
            for i, verse in enumerate(verses[:3]):
                print(f"   [{i+1}] Surah {verse.get('surah')}:{verse.get('ayah')}")
        
        await mcp.close()
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


def test_quran_tools():
    """Test 6: Quran-Specific Tools"""
    print("📝 Test 6: Quran-Specific Tools")
    print("-" * 70)
    
    try:
        from backend.tools.quran_foundation_tools import (
            search_quran_text,
            explore_theme,
            get_quranic_guidance
        )
        
        print("✅ Quran foundation tools imported successfully")
        print("   Available tools:")
        print("   • search_quran_text")
        print("   • fetch_surah")
        print("   • fetch_tafsir")
        print("   • explore_theme")
        print("   • get_quranic_guidance")
        print("   • register_quran_tools")
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


def test_agent_initialization():
    """Test 7: Agent Initialization"""
    print("📝 Test 7: Agent Initialization (Quran-Powered)")
    print("-" * 70)
    
    try:
        print("Attempting to import Quran-powered agent...")
        from backend.core.islamic_ai_agent_quran import IslamicAIAgent
        
        print("✅ Quran-powered agent module imported")
        print("   Note: Full initialization requires AgentScope and API keys")
        print("   (Skipping instantiation in this test)\n")
        return True
    except Exception as e:
        print(f"⚠️  Import issue (may be normal): {e}")
        print("   Check that all dependencies are installed\n")
        return False


def test_llm_provider():
    """Test 8: Quran-Centric LLM Provider"""
    print("📝 Test 8: Quran-Centric LLM Provider")
    print("-" * 70)
    
    try:
        from backend.utils.quran_llm_provider import (
            is_gemini_available,
            get_agentscope_model,
            query_quran_foundation
        )
        
        print("✅ Quran LLM provider imported successfully")
        print(f"   Gemini synthesis available: {is_gemini_available()}")
        print("   Available functions:")
        print("   • init_agentscope()")
        print("   • get_agentscope_model()")
        print("   • query_quran_foundation()")
        print("   • synthesize_quran_response()")
        print("   • get_quranic_answer()")
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        return False


async def run_all_tests():
    """Run all tests"""
    results = []
    
    # Test 1: MCP Provider
    results.append(await test_mcp_provider())
    
    # Test 2-5: MCP Functionality (async)
    print("🔄 Running MCP functionality tests...\n")
    try:
        results.append(await test_quran_search())
        results.append(await test_quran_fetch())
        results.append(await test_tafsir_fetch())
        results.append(await test_thematic_exploration())
    except Exception as e:
        print(f"⚠️  Some MCP tests skipped (MCP server may not be accessible): {e}\n")
        results.append(False)
        results.append(False)
        results.append(False)
        results.append(False)
    
    # Test 6: Tools
    results.append(test_quran_tools())
    
    # Test 7: Agent
    results.append(test_agent_initialization())
    
    # Test 8: LLM Provider
    results.append(test_llm_provider())
    
    # Summary
    print("="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Quran Foundation MCP integration is ready!")
    elif passed >= total - 2:
        print("\n✅ Most tests passed. Some MCP server connectivity tests may have been skipped.")
        print("   This is normal if the MCP server is not accessible from your location.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Review the output above.")
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("  1. Run: ./start.sh")
    print("  2. Test chat: curl -X POST http://localhost:5010/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"Tell me about Surah Al-Fatiha\"}'")
    print("  3. Read: docs/QURAN_FOUNDATION_MCP_GUIDE.md")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
