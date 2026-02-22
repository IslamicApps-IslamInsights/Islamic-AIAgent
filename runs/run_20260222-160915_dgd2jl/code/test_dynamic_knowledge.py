#!/usr/bin/env python3
"""
Test Script for Dynamic Islamic Knowledge Base
Demonstrates the enhanced API-based knowledge system
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_islamic_tools import (
    get_quran_verse,
    get_hadith,
    search_islamic_content,
    get_islamic_guidance,
    get_daily_islamic_content,
    get_prayer_times,
    get_qibla_direction,
    get_hijri_date,
    get_dua,
    get_surah_info
)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🌟 {title}")
    print('='*60)

def print_result(tool_name: str, result: str):
    """Print formatted result"""
    print(f"\n🔧 **{tool_name}**")
    print("-" * 40)
    print(result)
    print("-" * 40)

async def test_dynamic_knowledge():
    """Test all dynamic knowledge base functions"""
    
    print("🌟 Testing Dynamic Islamic Knowledge Base")
    print("=" * 60)
    print("This script tests the enhanced API-based Islamic knowledge system")
    print("All content is fetched from authentic Islamic sources dynamically")
    print("=" * 60)
    
    # Test 1: Quran Verses
    print_section("QURAN VERSES (Al-Quran Cloud API)")
    
    test_verses = [
        "2:255",      # Ayat al-Kursi
        "1:1",        # Al-Fatiha
        "al-fatiha",  # Special name
        "112:1"       # Al-Ikhlas
    ]
    
    for verse in test_verses:
        try:
            result = get_quran_verse(verse)
            print_result(f"get_quran_verse('{verse}')", result)
        except Exception as e:
            print(f"❌ Error testing verse {verse}: {e}")
    
    # Test 2: Hadith Collection
    print_section("HADITH COLLECTION (Hadith APIs)")
    
    test_topics = [
        "kindness",
        "prayer", 
        "charity",
        None  # Random hadith
    ]
    
    for topic in test_topics:
        try:
            topic_str = topic if topic else "random"
            result = get_hadith(topic)
            print_result(f"get_hadith('{topic_str}')", result)
        except Exception as e:
            print(f"❌ Error testing hadith topic {topic}: {e}")
    
    # Test 3: Search Functionality
    print_section("SEARCH ISLAMIC CONTENT")
    
    search_queries = [
        "patience",
        "charity",
        "prayer"
    ]
    
    for query in search_queries:
        try:
            result = search_islamic_content(query)
            print_result(f"search_islamic_content('{query}')", result)
        except Exception as e:
            print(f"❌ Error searching for {query}: {e}")
    
    # Test 4: Islamic Guidance
    print_section("COMPREHENSIVE ISLAMIC GUIDANCE")
    
    guidance_topics = [
        "patience",
        "charity",
        "prayer"
    ]
    
    for topic in guidance_topics:
        try:
            result = get_islamic_guidance(topic)
            print_result(f"get_islamic_guidance('{topic}')", result)
        except Exception as e:
            print(f"❌ Error getting guidance on {topic}: {e}")
    
    # Test 5: Daily Content
    print_section("DAILY ISLAMIC CONTENT")
    
    try:
        result = get_daily_islamic_content()
        print_result("get_daily_islamic_content()", result)
    except Exception as e:
        print(f"❌ Error getting daily content: {e}")
    
    # Test 6: Location-based Services
    print_section("LOCATION-BASED SERVICES")
    
    # Test coordinates (New York City)
    test_lat, test_lon = 40.7128, -74.0060
    
    try:
        prayer_result = get_prayer_times(test_lat, test_lon)
        print_result(f"get_prayer_times({test_lat}, {test_lon})", prayer_result)
    except Exception as e:
        print(f"❌ Error getting prayer times: {e}")
    
    try:
        qibla_result = get_qibla_direction(test_lat, test_lon)
        print_result(f"get_qibla_direction({test_lat}, {test_lon})", qibla_result)
    except Exception as e:
        print(f"❌ Error getting Qibla direction: {e}")
    
    # Test 7: Calendar and Duas
    print_section("CALENDAR & DUAS")
    
    try:
        hijri_result = get_hijri_date()
        print_result("get_hijri_date()", hijri_result)
    except Exception as e:
        print(f"❌ Error getting Hijri date: {e}")
    
    test_duas = ["morning", "evening", "travel"]
    for dua_occasion in test_duas:
        try:
            dua_result = get_dua(dua_occasion)
            print_result(f"get_dua('{dua_occasion}')", dua_result)
        except Exception as e:
            print(f"❌ Error getting {dua_occasion} dua: {e}")
    
    # Test 8: Surah Information
    print_section("SURAH INFORMATION")
    
    test_surahs = ["Al-Fatiha", "1", "Al-Baqarah"]
    for surah in test_surahs:
        try:
            surah_result = get_surah_info(surah)
            print_result(f"get_surah_info('{surah}')", surah_result)
        except Exception as e:
            print(f"❌ Error getting surah info for {surah}: {e}")

def test_sync_functions():
    """Test synchronous functions that don't require async"""
    
    print_section("SYNCHRONOUS FUNCTIONS TEST")
    
    # Test location-based functions
    test_lat, test_lon = 40.7128, -74.0060  # New York City
    
    functions_to_test = [
        ("get_hijri_date", lambda: get_hijri_date()),
        ("get_prayer_times", lambda: get_prayer_times(test_lat, test_lon)),
        ("get_qibla_direction", lambda: get_qibla_direction(test_lat, test_lon)),
        ("get_dua('morning')", lambda: get_dua('morning')),
        ("get_surah_info('1')", lambda: get_surah_info('1')),
    ]
    
    for func_name, func in functions_to_test:
        try:
            result = func()
            print_result(func_name, result)
        except Exception as e:
            print(f"❌ Error testing {func_name}: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Dynamic Islamic Knowledge Base Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test synchronous functions first
    test_sync_functions()
    
    # Test async functions
    print("\n🔄 Running async tests...")
    try:
        asyncio.run(test_dynamic_knowledge())
    except Exception as e:
        print(f"❌ Error running async tests: {e}")
    
    print_section("TEST SUMMARY")
    print("✅ Dynamic Islamic Knowledge Base testing completed!")
    print("📊 **Key Features Tested:**")
    print("   • Quran verses from Al-Quran Cloud API")
    print("   • Authentic Hadith from verified collections")
    print("   • Search functionality across both sources")
    print("   • Comprehensive Islamic guidance")
    print("   • Location-based prayer times and Qibla")
    print("   • Hijri calendar integration")
    print("   • Authentic Duas collection")
    print("   • Surah information database")
    print("\n🌟 **All content is fetched from authentic Islamic sources!**")
    print("🤲 May Allah bless this knowledge and make it beneficial for the Ummah!")

if __name__ == "__main__":
    main()
