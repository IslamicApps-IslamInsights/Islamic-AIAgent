# 🔍 Islamic AI Agent - Search Modes Guide

## Overview
The Islamic AI Agent provides **4 distinct search modes** to help users get the most relevant and accurate Islamic guidance. Each mode is specifically designed for different types of Islamic queries.

---

## 🎯 Search Modes Explained

### 1. 💬 **General Chat Mode** (Default)
**Purpose:** General Islamic questions and conversations

**Best for:**
- Basic Islamic questions
- General guidance requests
- Mixed topics in one query
- Casual Islamic conversations

**Examples:**
- "What are the five pillars of Islam?"
- "How do I pray?"
- "Tell me about Islamic finance"
- "What is halal food?"

**Response Type:** Comprehensive answers drawing from all Islamic sources

---

### 2. 📖 **Quran Search Mode**
**Purpose:** Specific Quran verse searches and Quranic guidance

**Best for:**
- Finding specific verses
- Searching by Surah names
- Thematic Quran searches
- Tafsir and commentary requests

**Search Options:**
- **Verse References:** `2:255`, `Al-Fatiha:1-7`, `Yasin:1-83`
- **Surah Names:** `Al-Fatiha`, `Yasin`, `Al-Ikhlas`
- **Topics:** `patience in Quran`, `charity verses`, `prayer guidance`
- **Arabic Terms:** `صبر`, `الصلاة`, `الزكاة`

**Examples:**
- "Ayat al-Kursi"
- "Surah Al-Fatiha with tafsir"
- "Verses about patience"
- "2:255"

**Response Features:**
- Arabic text with diacritics
- Accurate transliteration
- Multiple translations
- Classical tafsir (Ibn Kathir, Tabari)
- Historical context
- Cross-references
- Audio recitation options

---

### 3. ⭐ **Hadith Search Mode**
**Purpose:** Authentic Hadith searches and Prophetic guidance

**Best for:**
- Finding specific hadith
- Searching by topics
- Narrator-based searches
- Authenticity verification

**Search Options:**
- **Topics:** `kindness`, `charity`, `prayer`, `family`
- **Narrators:** `Abu Huraira`, `Aisha`, `Ibn Umar`
- **Collections:** `Sahih Bukhari`, `Sahih Muslim`, `Sunan Abu Dawud`
- **Authenticity:** `Sahih`, `Hasan`, `Da'if`

**Examples:**
- "Hadith about kindness"
- "Abu Huraira narrations about prayer"
- "Sahih Bukhari charity hadith"
- "Authentic hadith on parents"

**Response Features:**
- Complete Arabic text
- Accurate translations
- Full source citations (Collection, Book, Number)
- Narrator chain (Isnad) information
- Authenticity grades with explanations
- Cross-collection references
- Historical context

---

### 4. 👨‍🏫 **Ask Scholar Mode**
**Purpose:** Complex Islamic jurisprudence and scholarly consultation

**Best for:**
- Fiqh (Islamic law) questions
- Contemporary Islamic issues
- Madhab differences
- Complex religious rulings

**Specialized Scholars:**
- **Sheikh Abdullah:** Quran & Tafsir specialist
- **Sheikh Aisha:** Hadith & Sunnah expert
- **Sheikh Omar:** Fiqh & Islamic law
- **Sheikh Fatima:** Spiritual guidance
- **Imam Hassan:** General coordinator

**Examples:**
- "Is cryptocurrency trading halal?"
- "Prayer rules during airplane travel"
- "Modern banking in Islamic law"
- "Social media guidelines in Islam"

**Response Features:**
- Scholarly methodology
- Evidence from Quran and Hadith
- Madhab comparisons (Hanafi, Maliki, Shafi'i, Hanbali)
- Contemporary applications
- Practical implementation guidance

---

## 🎨 User Interface Features

### Search Mode Selector
Located above the input field with clear visual indicators:
- **💬 General Chat** - Default green highlight
- **📖 Quran Search** - Green theme with book icon
- **⭐ Hadith Search** - Yellow theme with star icon
- **👨‍🏫 Ask Scholar** - Red theme with scholar icon

### Dynamic Input Placeholders
The input field changes based on selected mode:
- **General:** "Ask about Islam: prayers, Quran, halal food, duas..."
- **Quran:** "Search Quran: verse reference (2:255), surah name, or topic..."
- **Hadith:** "Search Hadith: topic, narrator, collection, or authenticity grade..."
- **Scholar:** "Ask Islamic Scholar: fiqh, aqeedah, contemporary issues..."

### Contextual Sample Questions
Sample questions update based on search mode:
- **General:** Basic Islamic topics
- **Quran:** Verse references and Surah names
- **Hadith:** Hadith topics and collections
- **Scholar:** Contemporary Islamic issues

### Response Indicators
Each response shows a colored badge indicating the search mode used:
- 📖 **Quran Search** - Green badge
- ⭐ **Hadith Search** - Yellow badge
- 👨‍🏫 **Scholar Consultation** - Red badge
- 💬 **General Response** - Blue badge

---

## 🔄 How It Works Technically

### Backend Routing
1. **General Chat** → `/api/chat` endpoint
2. **Quran Search** → `/api/chat` with `[QURAN SEARCH]` prefix
3. **Hadith Search** → `/api/chat` with `[HADITH SEARCH]` prefix
4. **Scholar Mode** → `/api/scholar` endpoint with specialized AI agents

### AI Agent Selection
- **General queries** → Main Islamic AI agent
- **Quran searches** → Enhanced with Quran-specific context
- **Hadith searches** → Enhanced with Hadith-specific context
- **Scholar questions** → Routed to appropriate specialist scholar

### Response Enhancement
Each mode provides:
- **Specialized formatting** for the content type
- **Relevant cross-references** within the same domain
- **Appropriate citations** and sources
- **Context-aware suggestions** for follow-up questions

---

## 💡 Best Practices for Users

### When to Use Each Mode

**Use General Chat when:**
- You're not sure which category your question fits
- You want a broad overview of a topic
- You're asking about multiple Islamic topics
- You want conversational responses

**Use Quran Search when:**
- You know the specific verse or Surah
- You want detailed tafsir and commentary
- You're studying Quranic themes
- You need Arabic text with translations

**Use Hadith Search when:**
- You're looking for Prophetic guidance on specific topics
- You want to verify hadith authenticity
- You're researching specific narrators
- You need complete source citations

**Use Ask Scholar when:**
- You have complex fiqh questions
- You need contemporary Islamic rulings
- You want to understand madhab differences
- You're dealing with modern Islamic issues

### Search Tips

**For Quran Search:**
- Use specific verse numbers (e.g., "2:255")
- Try both Arabic and English Surah names
- Use thematic keywords for topic searches
- Combine terms for better results

**For Hadith Search:**
- Specify the collection if known
- Use topic keywords rather than exact phrases
- Include narrator names for specific searches
- Ask about authenticity grades when uncertain

**For Scholar Consultation:**
- Be specific about your situation
- Provide relevant context
- Mention your location/madhab if relevant
- Ask follow-up questions for clarification

---

## 🎯 Expected Response Quality

### Quran Responses Include:
- ✅ Original Arabic text with proper diacritics
- ✅ Accurate transliteration for pronunciation
- ✅ Multiple authentic translations
- ✅ Classical tafsir from renowned scholars
- ✅ Historical context and revelation circumstances
- ✅ Practical applications and spiritual lessons
- ✅ Cross-references to related verses

### Hadith Responses Include:
- ✅ Complete Arabic text of the hadith
- ✅ Accurate English translation
- ✅ Full source citation (Collection, Book, Number)
- ✅ Narrator chain information
- ✅ Authenticity grade with explanation
- ✅ Scholarly commentary and context
- ✅ Practical applications in modern life

### Scholar Responses Include:
- ✅ Evidence-based rulings from Quran and Hadith
- ✅ Comparison of different madhab opinions
- ✅ Contemporary applications and considerations
- ✅ Practical implementation guidance
- ✅ Recommendations for further consultation
- ✅ Scholarly humility and appropriate disclaimers

---

## 🚀 Advanced Features

### Audio Integration
- Quran verses include audio recitation options
- Multiple renowned reciters available
- Proper Tajweed pronunciation
- Play/pause controls for learning

### Bookmark System
- Save favorite verses and hadith
- Visual indicators for saved content
- Easy access to bookmarked items
- Personal study collection

### Cross-References
- Related verses and hadith suggestions
- Thematic connections across sources
- Progressive learning pathways
- Comprehensive topic coverage

---

*This guide helps users maximize the Islamic AI Agent's capabilities by choosing the right search mode for their specific needs, ensuring accurate, relevant, and comprehensive Islamic guidance.*
