import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.llm_provider import init_agentscope
from backend.core.islamic_ai_agent_quran import IslamicAIAgent
from backend.core.multi_agent_islamic_system import IslamicMultiAgentSystem


def _memory_mb():
    try:
        import psutil

        proc = psutil.Process()
        return proc.memory_info().rss / 1024 / 1024
    except Exception:
        return None


def diagnose():
    try:
        mem0 = _memory_mb()
        if mem0 is not None:
            print(f"Memory: {mem0:.0f}MB")

        print("1. Initializing AgentScope...")
        init_agentscope()
        print("✅ AgentScope initialized.")

        mem1 = _memory_mb()
        if mem1 is not None:
            print(f"Memory: {mem1:.0f}MB")

        print("2. Initializing Single Agent (Quran-first)...")
        IslamicAIAgent()
        print("✅ Single Agent initialized.")

        mem2 = _memory_mb()
        if mem2 is not None:
            print(f"Memory: {mem2:.0f}MB")

        print("3. Initializing Multi-Agent System...")
        IslamicMultiAgentSystem()
        print("✅ Multi-Agent System initialized.")

        mem3 = _memory_mb()
        if mem3 is not None:
            print(f"Memory: {mem3:.0f}MB")

        print("\n✨ ALL INITIALIZATIONS SUCCESSFUL!")
    except Exception as e:
        print(f"\n❌ ERROR during diagnostic: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose()
