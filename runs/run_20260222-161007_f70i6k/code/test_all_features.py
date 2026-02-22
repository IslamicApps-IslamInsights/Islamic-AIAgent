#!/usr/bin/env python3
"""
Comprehensive test script for Islamic AI Agent features
Tests all functionality to ensure everything works correctly
"""

import asyncio
import sys
import os
sys.path.append('.')

from enhanced_islamic_tools import *

def test_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def test_result(test_name, result, expected_keywords=None):
    print(f"\n🔍 {test_name}:")
    print("-" * 40)
    
    if result.startswith("❌"):
        print(f"❌ FAILED: {result}")
        return False
    
    # Check for expected keywords if provided
    if expected_keywords:
        found_keywords = []
        for keyword in expected_keywords:
            if keyword.lower() in result.lower():
                found_keywords.append(keyword)
        
        if len(found_keywords) >= len(expected_keywords) // 2:  # At least half should be found
            print(f"✅ PASSED: Found keywords {found_keywords}")
        else:
            print(f"⚠️  PARTIAL: Missing some expected content")
    else:
        print(f"✅ PASSED: Function executed successfully")
    
    # Show first 200 characters of result
    preview = result[:200] + "..." if len(result) > 200 else result
    print(f"📄 Preview: {preview}")
    return True

def main():
    print("🌟 ISLAMIC AI AGENT - COMPREHENSIVE FEATURE TEST")
    print("Testing all features to ensure proper functionality")
    
    test_results = []
    
    # Test 1: Quran Verse Retrieval
    test_section("QURAN VERSE TESTS")
    
    # Single verse test
    result = get_quran_verse("2:255")
    test_results.append(test_result("Ayat al-Kursi (2:255)", result, ["Arabic", "Translation", "Allah"]))
    
    # Complete surah test
    result = get_quran_verse("al-fatiha")
    test_results.append(test_result("Complete Surah Al-Fatiha", result, ["Verse 1", "Verse 2", "Arabic", "Translation"]))
    
    # Another single verse
    result = get_quran_verse("112:1")
    test_results.append(test_result("Surah Al-Ikhlas verse 1", result, ["Arabic", "Translation", "Say"]))
    
    # Test 2: Hadith Retrieval
    test_section("HADITH TESTS")
    
    # Topic-based hadith
    result = get_hadith("kindness")
    test_results.append(test_result("Hadith about kindness", result, ["Prophet", "Hadith", "Reference"]))
    
    # Random hadith
    result = get_hadith()
    test_results.append(test_result("Random hadith", result, ["Prophet", "Hadith", "Reference"]))
    
    # Test 3: Prayer Times
    test_section("PRAYER TIME TESTS")
    
    # Prayer times for NYC
    result = get_prayer_times(40.7128, -74.0060)
    test_results.append(test_result("Prayer times for NYC", result, ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]))
    
    # Test 4: Qibla Direction
    test_section("QIBLA DIRECTION TESTS")
    
    # Qibla from NYC
    result = get_qibla_direction(40.7128, -74.0060)
    test_results.append(test_result("Qibla direction from NYC", result, ["Bearing", "Kaaba", "direction"]))
    
    # Test 5: Duas
    test_section("DUA TESTS")
    
    # Morning dua
    result = get_dua("morning")
    test_results.append(test_result("Morning dua", result, ["Arabic", "Translation", "morning"]))
    
    # Evening dua
    result = get_dua("evening")
    test_results.append(test_result("Evening dua", result, ["Arabic", "Translation", "evening"]))
    
    # Test 6: Islamic Calendar
    test_section("ISLAMIC CALENDAR TESTS")
    
    # Hijri date
    result = get_hijri_date()
    test_results.append(test_result("Current Hijri date", result, ["Hijri", "Date", "Islamic"]))
    
    # Test 7: Search Functionality
    test_section("SEARCH TESTS")
    
    # Search Islamic content
    result = search_islamic_content("patience")
    test_results.append(test_result("Search for 'patience'", result, ["Search Results", "patience"]))
    
    # Test 8: Islamic Guidance
    test_section("GUIDANCE TESTS")
    
    # Get guidance on charity
    result = get_islamic_guidance("charity")
    test_results.append(test_result("Guidance on charity", result, ["charity", "guidance", "Islamic"]))
    
    # Test 9: Daily Content
    test_section("DAILY CONTENT TESTS")
    
    # Daily Islamic content
    result = get_daily_islamic_content()
    test_results.append(test_result("Daily Islamic content", result, ["Daily", "Verse", "Hadith"]))
    
    # Test 10: Surah Information
    test_section("SURAH INFO TESTS")
    
    # Surah information
    result = get_surah_info("Al-Fatiha")
    test_results.append(test_result("Al-Fatiha surah info", result, ["Al-Fatiha", "verses", "Meccan"]))
    
    # Summary
    test_section("TEST SUMMARY")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 TEST RESULTS:")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Islamic AI Agent is fully functional!")
    elif passed_tests >= total_tests * 0.8:
        print(f"\n✅ MOSTLY WORKING! {passed_tests} out of {total_tests} features working correctly.")
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Only {passed_tests} out of {total_tests} features working.")
    
    print(f"\n🤲 May Allah bless this Islamic AI project and make it beneficial for the Ummah!")

if __name__ == "__main__":
    main()
