"""
Islamic AI Agent - Best Practices Validation Script
Verify that all components are correctly implemented
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Validation")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

class ValidationReport:
    def __init__(self):
        self.checks = []
        self.status = "PASS"
    
    def add_check(self, name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.checks.append({
            "name": name,
            "passed": passed,
            "details": details,
            "status": status
        })
        if not passed:
            self.status = "FAIL"
    
    def print_report(self):
        print("\n" + "="*80)
        print("Islamic AI Agent - Best Practices Validation Report")
        print("="*80)
        
        for check in self.checks:
            print(f"\n{check['status']} | {check['name']}")
            if check['details']:
                print(f"     {check['details']}")
        
        print("\n" + "="*80)
        print(f"Overall Status: {self.status}")
        print("="*80 + "\n")
    
    def save_report(self):
        report_file = os.path.join(PROJECT_ROOT, "validation_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "status": self.status,
                "checks": self.checks
            }, f, indent=2)
        logger.info(f"Report saved to: {report_file}")


def validate_files():
    """Check that all required best practices files exist"""
    report = ValidationReport()
    
    # Ingestion pipeline
    ingestion_file = os.path.join(PROJECT_ROOT, "backend/knowledge/ingest_best_practices.py")
    ingestion_exists = os.path.exists(ingestion_file)
    report.add_check(
        "Ingestion Pipeline (ingest_best_practices.py)",
        ingestion_exists,
        f"Location: {ingestion_file}" if ingestion_exists else f"Not found: {ingestion_file}"
    )
    
    # LLM Best Practices
    llm_file = os.path.join(PROJECT_ROOT, "backend/utils/llm_best_practices.py")
    llm_exists = os.path.exists(llm_file)
    report.add_check(
        "LLM Configuration (llm_best_practices.py)",
        llm_exists,
        f"Location: {llm_file}" if llm_exists else f"Not found: {llm_file}"
    )
    
    # Documentation
    docs_file = os.path.join(PROJECT_ROOT, "docs/BEST_PRACTICES_IMPLEMENTATION.md")
    docs_exists = os.path.exists(docs_file)
    report.add_check(
        "Best Practices Documentation",
        docs_exists,
        f"Location: {docs_file}" if docs_exists else f"Not found: {docs_file}"
    )
    
    # Requirements
    req_file = os.path.join(PROJECT_ROOT, "requirements_best_practices.txt")
    req_exists = os.path.exists(req_file)
    report.add_check(
        "Best Practices Requirements",
        req_exists,
        f"Location: {req_file}" if req_exists else f"Not found: {req_file}"
    )
    
    # Setup script
    setup_file = os.path.join(PROJECT_ROOT, "setup_best_practices.sh")
    setup_exists = os.path.exists(setup_file)
    report.add_check(
        "Setup Script",
        setup_exists,
        f"Location: {setup_file}" if setup_exists else f"Not found: {setup_file}"
    )
    
    return report


def validate_dependencies():
    """Check that required dependencies are installed"""
    report = ValidationReport()
    
    dependencies = [
        ("langchain", "Core RAG framework"),
        ("langchain_community", "LangChain community modules"),
        ("rank_bm25", "BM25 search implementation"),
        ("nltk", "NLP tokenization"),
        ("transformers", "HuggingFace models"),
        ("chromadb", "Vector database"),
        ("google.generativeai", "Gemini API"),
        ("anthropic", "Claude API"),
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            report.add_check(
                f"Dependency: {module_name}",
                True,
                description
            )
        except ImportError:
            report.add_check(
                f"Dependency: {module_name}",
                False,
                f"{description} - Not installed"
            )
    
    return report


def validate_data_setup():
    """Check that data directories are set up"""
    report = ValidationReport()
    
    # Data directory
    data_dir = os.path.join(PROJECT_ROOT, "backend/knowledge/data")
    data_exists = os.path.exists(data_dir)
    report.add_check(
        "Data Directory",
        data_exists,
        f"Location: {data_dir}"
    )
    
    if data_exists:
        json_files = len(list(Path(data_dir).glob("*.json")))
        txt_files = len(list(Path(data_dir).glob("*.txt")))
        
        report.add_check(
            "Data Files Present",
            json_files + txt_files > 0,
            f"JSON: {json_files}, TXT: {txt_files}"
        )
    
    # Vector DB directory
    chroma_dir = os.path.join(PROJECT_ROOT, "backend/knowledge/chroma_db")
    chroma_exists = os.path.exists(chroma_dir)
    report.add_check(
        "Vector DB Directory",
        chroma_exists,
        f"Location: {chroma_dir} (Created during first ingestion)"
    )
    
    # BM25 index
    bm25_file = os.path.join(PROJECT_ROOT, "backend/knowledge/bm25_index.pkl")
    bm25_exists = os.path.exists(bm25_file)
    
    size_mb = 0
    if bm25_exists:
        size_mb = os.path.getsize(bm25_file) / 1024 / 1024
    
    report.add_check(
        "BM25 Index",
        bm25_exists,
        f"Size: {size_mb:.1f}MB" if bm25_exists else "Not created yet (run ingestion)"
    )
    
    return report


def validate_api():
    """Check that API is running and responding"""
    report = ValidationReport()
    
    try:
        import requests
        
        # Check backend
        try:
            response = requests.get("http://localhost:5010/api/health", timeout=2)
            backend_ok = response.status_code == 200
            
            if backend_ok:
                data = response.json()
                agents_ready = data.get('agents_ready', False)
                rag_ready = data.get('services', {}).get('rag_ready', False)
                
                report.add_check(
                    "Backend API (http://localhost:5010)",
                    True,
                    f"Agents ready: {agents_ready}, RAG ready: {rag_ready}"
                )
            else:
                report.add_check(
                    "Backend API (http://localhost:5010)",
                    False,
                    f"Status code: {response.status_code}"
                )
        except requests.ConnectionError:
            report.add_check(
                "Backend API (http://localhost:5010)",
                False,
                "Connection refused - Backend not running"
            )
        except requests.Timeout:
            report.add_check(
                "Backend API",
                False,
                "Timeout - Backend may be starting"
            )
        
        # Check frontend
        try:
            response = requests.get("http://localhost:3001", timeout=2)
            report.add_check(
                "Frontend (http://localhost:3001)",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except requests.ConnectionError:
            report.add_check(
                "Frontend (http://localhost:3001)",
                False,
                "Connection refused - Frontend not running"
            )
    
    except ImportError:
        report.add_check(
            "API Tests",
            False,
            "Requests library not installed - Skipping API checks"
        )
    
    return report


def validate_configuration():
    """Check environment configuration"""
    report = ValidationReport()
    
    # Check .env file
    env_file = os.path.join(PROJECT_ROOT, ".env")
    env_exists = os.path.exists(env_file)
    report.add_check(
        ".env Configuration File",
        env_exists,
        f"Location: {env_file}"
    )
    
    # Check API keys
    import os as os_module
    from dotenv import load_dotenv
    
    if env_exists:
        load_dotenv(env_file)
    
    gemini_key = bool(os_module.getenv('GOOGLE_API_KEY'))
    claude_key = bool(os_module.getenv('ANTHROPIC_API_KEY'))
    
    report.add_check(
        "Gemini API Key (GOOGLE_API_KEY)",
        gemini_key,
        "Configured" if gemini_key else "Not set (optional)"
    )
    
    report.add_check(
        "Claude API Key (ANTHROPIC_API_KEY)",
        claude_key,
        "Configured" if claude_key else "Not set (optional)"
    )
    
    at_least_one = gemini_key or claude_key
    report.add_check(
        "LLM Synthesis Available",
        at_least_one,
        "At least one LLM API configured" if at_least_one else "Configure Gemini or Claude"
    )
    
    return report


def main():
    """Run all validation checks"""
    print("\n🔍 Validating Islamic AI Agent - Best Practices Implementation\n")
    
    all_reports = [
        ("Files & Structure", validate_files()),
        ("Dependencies", validate_dependencies()),
        ("Data Setup", validate_data_setup()),
        ("Configuration", validate_configuration()),
        ("API Status", validate_api()),
    ]
    
    overall_status = "PASS"
    
    for section_name, report in all_reports:
        print(f"\n{section_name}")
        print("-" * 50)
        report.print_report()
        if report.status == "FAIL":
            overall_status = "FAIL"
    
    # Save consolidated report
    print("\n📊 Saving consolidated validation report...\n")
    
    consolidated = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "sections": [
            {
                "name": section_name,
                "status": report.status,
                "checks": report.checks
            }
            for section_name, report in all_reports
        ]
    }
    
    report_file = os.path.join(PROJECT_ROOT, "validation_report.json")
    with open(report_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"✅ Validation report saved to: {report_file}")
    
    # Final recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80 + "\n")
    
    if overall_status == "PASS":
        print("✅ All validation checks passed!")
        print("\nNext steps:")
        print("1. Run ingestion: python backend/knowledge/ingest_best_practices.py")
        print("2. Start backend: python backend/api/web_api.py")
        print("3. Start frontend: cd frontend && npm run dev -- --port 3001")
        print("4. Visit: http://localhost:3001")
    else:
        print("⚠️  Some validation checks failed")
        print("\nResolve issues:")
        print("1. Review validation_report.json for details")
        print("2. Install missing dependencies: pip install -r requirements_best_practices.txt")
        print("3. Set up configuration in .env file")
        print("4. Add Islamic knowledge data to backend/knowledge/data/")
        print("5. Re-run validation: python validate_best_practices.py")
    
    print("\n📖 Read docs/BEST_PRACTICES_IMPLEMENTATION.md for detailed guidance")
    print("="*80 + "\n")
    
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
