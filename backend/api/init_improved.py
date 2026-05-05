"""
Improved agent initialization with fallback strategies
"""

# Global state
single_agent = None
multi_agent_system = None
agent_initialized = False
initialization_status = {
    'single_agent': False,
    'multi_agent': False,
    'knowledge_base': False,
    'errors': []
}


def initialize_agents_improved():
    """Initialize AI agents with graceful degradation"""
    global single_agent, multi_agent_system, agent_initialized
    global initialization_status
    
    initialization_status = {
        'single_agent': False,
        'multi_agent': False,
        'knowledge_base': False,
        'errors': []
    }
    
    print("🚀 Initializing Islamic AI Agents (Improved Mode)...")
    
    # Step 1: Initialize LLM provider
    try:
        print("📡 Setting up LLM provider...")
        from backend.utils.llm_provider import init_agentscope
        init_agentscope()
        print("✅ LLM provider configured")
    except Exception as e:
        error_msg = f"LLM initialization failed: {e}"
        print(f"⚠️  {error_msg}")
        initialization_status['errors'].append(error_msg)
        # Continue anyway - single agent might still work
    
    # Step 2: Initialize single agent (critical)
    try:
        print("📱 Initializing single agent...")
        from backend.core.islamic_ai_agent import IslamicAIAgent
        single_agent = IslamicAIAgent()
        initialization_status['single_agent'] = True
        print("✅ Single agent ready!")
    except Exception as e:
        error_msg = f"Single agent initialization failed: {e}"
        print(f"❌ {error_msg}")
        initialization_status['errors'].append(error_msg)
        single_agent = None
    
    # Step 3: Initialize multi-agent system (preferred but not critical)
    try:
        print("👥 Initializing multi-agent system...")
        from backend.core.multi_agent_islamic_system import (
            IslamicMultiAgentSystem,
        )
        multi_agent_system = IslamicMultiAgentSystem()
        initialization_status['multi_agent'] = True
        print("✅ Multi-agent system ready!")
    except Exception as e:
        error_msg = f"Multi-agent system initialization failed: {e}"
        print(f"⚠️  {error_msg}")
        initialization_status['errors'].append(error_msg)
        multi_agent_system = None
        # Fall back to single agent
        if single_agent:
            print("📌 Falling back to single agent mode")
    
    # Step 4: Initialize knowledge base (lazy, memory-safe)
    try:
        print("🕯️  Initializing Scholarly Knowledge Base (lazy)...")
        from backend.knowledge.memory_optimized_loader import (
            initialize_optimized_rag,
            get_memory_optimized_loader,
        )

        status = initialize_optimized_rag()
        _ = get_memory_optimized_loader()
        initialization_status["knowledge_base"] = bool(
            status.get("bm25_available") or status.get("chroma_available")
        )

        if initialization_status["knowledge_base"]:
            print("📖 Knowledge base ready (models load on first search)")
        else:
            print("⚠️  Knowledge base not available (no index/db found)")
            initialization_status["errors"].append("KB not available")
    except Exception as e:
        error_msg = f"Knowledge base initialization failed: {e}"
        print(f"⚠️  {error_msg}")
        initialization_status['errors'].append(error_msg)
    
    # Determine overall status
    if single_agent or multi_agent_system:
        agent_initialized = True
        print("\n🎉 AI Agents initialized successfully!")
        mode = "Multi-Agent" if multi_agent_system else "Single Agent"
        print(f"   Status: {mode} mode active")
        if initialization_status['errors']:
            warning_count = len(initialization_status["errors"])
            print(f"   ⚠️  {warning_count} warnings/issues (see logs)")
    else:
        agent_initialized = False
        print("\n❌ Critical: No agents could be initialized!")
        for error in initialization_status['errors']:
            print(f"   - {error}")
    
    return agent_initialized


def get_initialization_status():
    """Get detailed initialization status"""
    return {
        'initialized': agent_initialized,
        'single_agent': initialization_status['single_agent'],
        'multi_agent': initialization_status['multi_agent'],
        'knowledge_base': initialization_status['knowledge_base'],
        'error_count': len(initialization_status['errors']),
        'errors': initialization_status['errors'][:5]  # Last 5 errors
    }
