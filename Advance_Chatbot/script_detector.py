import re
import re
import unicodedata

class ScriptDetector:
    def __init__(self):
        # Define script patterns
        self.devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        self.latin_pattern = re.compile(r'[a-zA-Z]')
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        self.cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
        
        # Common romanized Hindi/Marathi words to help detection
        self.romanized_indic_indicators = [
            # Hindi indicators
            'kaise', 'kya', 'hai', 'hoon', 'aap', 'main', 'mera', 'tera', 'uska',
            'kahan', 'kab', 'kaun', 'kitna', 'kyun', 'phir', 'abhi', 'yahan',
            'wahan', 'kal', 'aaj', 'agar', 'lekin', 'aur', 'ya', 'ke', 'ki',
            'ko', 'se', 'me', 'par', 'tak', 'bhi', 'nahi', 'sirf', 'bas',
            'kar', 'karta', 'karte', 'karna', 'karega', 'karenge', 'tha', 'thi', 'the',
            'hoga', 'hogi', 'honge', 'gaya', 'gayi', 'gaye', 'raha', 'rahi', 'rahe',
            'dikh', 'dekh', 'suna', 'bola', 'kaha', 'pata', 'malum', 'samaj',
            
            # Marathi indicators
            'kasa', 'kay', 'aahe', 'mala', 'tumcha', 'tyacha', 'kuthe', 'keli',
            'karto', 'kartoy', 'pahije', 'hoy', 'nako', 'bara', 'chalu', 'kshan',
            'mhanje', 'ani', 'pan', 'tar', 'mag', 'sagla', 'khup', 'thoda',
            'ata', 'purna', 'sampla', 'zala', 'zali', 'zale', 'kela', 'keli', 'kele',
            'gela', 'geli', 'gele', 'ala', 'ali', 'ale', 'rahila', 'rahili', 'rahile',
            'tula', 'tyala', 'tyala', 'amhi', 'tumhi', 'te', 'ti', 'tyanni',
            'mazyat', 'tuzyat', 'tyachyat', 'amchyat', 'tumchyat', 'tyanchyat',
            'mazha', 'tuzha', 'tyacha', 'amcha', 'tumcha', 'tyancha',
            'mi', 'tu', 'to', 'ti', 'aapan', 'aamhi', 'tumi', 'te',
            'kiti', 'kuthla', 'kotha', 'kshan', 'vel', 'divasa', 'mahina', 'varsha'
        ]
        
        # Specific Marathi patterns (both exact and partial matches)
        self.marathi_specific_words = [
            'aahe', 'nahi', 'hoy', 'ata', 'mag', 'pan', 'ani', 'kasa', 'kay',
            'kuthe', 'kiti', 'kshan', 'mala', 'tula', 'tyala', 'amhi', 'tumhi',
            'mazha', 'tuzha', 'tyacha', 'amcha', 'tumcha', 'tyancha',
            'karto', 'kartoy', 'kela', 'keli', 'kele', 'gela', 'geli', 'gele',
            'ala', 'ali', 'ale', 'zala', 'zali', 'zale', 'pahije', 'nako',
            # Additional Marathi patterns
            'maz', 'nab', 'ahe', 'taap', 'aaala', 'mla', 'hoaty', 'trass',
            'doke', 'dukhata', 'bara', 'khup', 'thoda', 'sampla', 'rahila',
            'tumhala', 'tyanchya', 'amchya', 'mazyat', 'tuzyat', 'tyachyat'
        ]
        
        # Hindi specific words (to differentiate from Marathi)
        self.hindi_specific_words = [
            'hai', 'hoon', 'hain', 'tha', 'thi', 'the', 'kya', 'kaise', 'kahan',
            'main', 'aap', 'yeh', 'woh', 'iska', 'uska', 'mera', 'tera',
            'kar', 'karta', 'karte', 'karna', 'karega', 'karenge',
            'gaya', 'gayi', 'gaye', 'raha', 'rahi', 'rahe', 'hoga', 'hogi', 'honge',
            # Additional Hindi patterns  
            'bukhar', 'sir', 'dard', 'theek', 'accha', 'kharab', 'bimar'
        ]
    
    def detect_indic_language(self, text):
        """Specifically detect Hindi vs Marathi for both scripts"""
        # Keep original text for Devanagari, use lowercase for Roman
        original_text = text
        text_lower = text.lower()
        words_original = original_text.split()
        words_lower = text_lower.split()
        
        # Count Marathi specific indicators
        marathi_score = 0
        
        # Additional Marathi patterns (flexible matching)
        marathi_patterns = ['ahe', 'aahe', 'mla', 'maz', 'nab', 'taap', 'aaala', 'hoaty', 'trass']
        hindi_patterns = ['hai', 'bukhar', 'sir', 'dard', 'theek', 'main', 'mera']
        
        for word_orig, word_lower in zip(words_original, words_lower):
            # Exact matches
            if word_orig in self.marathi_specific_words or word_lower in self.marathi_specific_words:
                marathi_score += 2
            # Partial matches for Marathi
            elif any(pattern in word_lower for pattern in marathi_patterns):
                marathi_score += 1
            elif any(pattern in word_orig for pattern in ['आहे', 'नको', 'कसा', 'तुमचा', 'त्याचा', 'मला']):
                marathi_score += 2
        
        # Count Hindi specific indicators  
        hindi_score = 0
        for word_orig, word_lower in zip(words_original, words_lower):
            # Exact matches
            if word_orig in self.hindi_specific_words or word_lower in self.hindi_specific_words:
                hindi_score += 2
            # Partial matches for Hindi
            elif any(pattern in word_lower for pattern in hindi_patterns):
                hindi_score += 1
            elif any(pattern in word_orig for pattern in ['है', 'हूं', 'क्या', 'कैसे', 'मेरा', 'मैं']):
                hindi_score += 2
        
        # Additional Marathi patterns
        if 'आहे' in original_text or 'aahe' in text_lower: marathi_score += 3
        if 'नको' in original_text or 'nako' in text_lower: marathi_score += 2
        if 'कसा' in original_text or 'kasa' in text_lower: marathi_score += 2
        if ('मला' in original_text or 'mala' in text_lower) and ('तुम्ही' in original_text or 'tumhi' in text_lower): marathi_score += 2
        
        # Additional Hindi patterns
        if 'है' in original_text or 'hai' in text_lower: hindi_score += 3
        if 'हूं' in original_text or 'hoon' in text_lower: hindi_score += 2
        if 'क्या' in original_text or 'kya' in text_lower: hindi_score += 2
        if ('मैं' in original_text or 'main' in text_lower) and ('आप' in original_text or 'aap' in text_lower): hindi_score += 2
        
        # Decide based on scores - require minimum threshold
        if marathi_score > hindi_score and marathi_score > 2:  # Increased threshold
            return 'marathi'
        elif hindi_score > marathi_score and hindi_score > 2:  # Increased threshold
            return 'hindi'
        else:
            return 'unknown'
    
    def detect_script(self, text):
        """
        Detect the primary script used in the text
        Returns: 'devanagari', 'latin', 'arabic', 'cyrillic', 'mixed', or 'unknown'
        """
        if not text or not text.strip():
            return 'unknown'
        
        # Keep original text for language detection
        original_text = text.strip()
        # Clean text for script analysis only
        text_for_analysis = text.strip().lower()
        
        # Count characters in different scripts using original text
        devanagari_count = len(self.devanagari_pattern.findall(original_text))
        latin_count = len(self.latin_pattern.findall(original_text))
        arabic_count = len(self.arabic_pattern.findall(original_text))
        cyrillic_count = len(self.cyrillic_pattern.findall(original_text))
        
        total_chars = len([c for c in original_text if c.isalpha()])
        
        if total_chars == 0:
            return 'unknown'
        
        # Calculate percentages
        devanagari_pct = (devanagari_count / total_chars) * 100
        latin_pct = (latin_count / total_chars) * 100
        arabic_pct = (arabic_count / total_chars) * 100
        cyrillic_pct = (cyrillic_count / total_chars) * 100
        
        # Determine primary script
        if devanagari_pct > 70:
            # For Devanagari, try to detect Hindi vs Marathi using original text
            lang = self.detect_indic_language(original_text)  # Pass original text
            if lang == 'marathi':
                return 'devanagari_marathi'
            elif lang == 'hindi':
                return 'devanagari_hindi'
            else:
                return 'devanagari'  # Default
        elif latin_pct > 70:
            # Check if it's romanized Indic by first detecting language
            lang = self.detect_indic_language(original_text)  # Detect language first
            
            # If we detected specific language with reasonable confidence, it's likely romanized
            if lang == 'marathi':
                return 'romanized_marathi'
            elif lang == 'hindi':
                return 'romanized_hindi'
            
            # Fallback to pattern-based detection - but be more selective
            words = text_for_analysis.split()  # Use lowercase for pattern matching
            romanized_matches = sum(1 for word in words if word in self.romanized_indic_indicators)
            # Only consider it romanized if we have strong evidence
            if romanized_matches > 1 or (romanized_matches > 0 and self._has_indic_transliteration_pattern(text_for_analysis)):
                # Generic romanized if no specific language detected but patterns found
                return 'romanized_indic'
            return 'latin'
        elif arabic_pct > 70:
            return 'arabic'
        elif cyrillic_pct > 70:
            return 'cyrillic'
        elif devanagari_pct + latin_pct > 80:
            return 'mixed'
        else:
            return 'unknown'
    
    def _has_indic_transliteration_pattern(self, text):
        """Check for common transliteration patterns"""
        patterns = [
            r'\b\w*aa\w*\b',  # aa vowel
            r'\b\w*ee\w*\b',  # ee vowel
            r'\b\w*oo\w*\b',  # oo vowel
            r'\b\w*ch\w*\b',  # ch consonant
            r'\b\w*th\w*\b',  # th consonant
            r'\b\w*dh\w*\b',  # dh consonant
            r'\b\w*gh\w*\b',  # gh consonant
            r'\b\w*kh\w*\b',  # kh consonant
        ]
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, text):
                matches += 1
        
        return matches >= 2
    
    def create_script_instruction(self, detected_script, user_text):
        """Create instruction for AI to maintain the same script"""
        
        base_instruction = f"""
CRITICAL SCRIPT PRESERVATION RULE:
User input script detected: {detected_script.upper()}
"""
        
        if detected_script in ['devanagari', 'devanagari_hindi', 'devanagari_marathi']:
            lang_hint = ""
            if detected_script == 'devanagari_hindi':
                lang_hint = "\n- Language detected as HINDI"
            elif detected_script == 'devanagari_marathi':
                lang_hint = "\n- Language detected as MARATHI"
                
            return base_instruction + f"""
- User has written in DEVANAGARI script{lang_hint}
- You MUST respond in DEVANAGARI script only
- DO NOT use Latin/Roman letters
- Use proper Devanagari characters: अ, आ, इ, ई, etc.
- Respond in the SAME LANGUAGE (Hindi/Marathi) as user input
"""
        
        elif detected_script in ['romanized_indic', 'romanized_hindi', 'romanized_marathi']:
            lang_hint = ""
            if detected_script == 'romanized_hindi':
                lang_hint = "\n- Language detected as HINDI in Roman script"
            elif detected_script == 'romanized_marathi':
                lang_hint = "\n- Language detected as MARATHI in Roman script"
                
            return base_instruction + f"""
- User has written in ROMANIZED/LATIN script (Hindi/Marathi in English letters){lang_hint}
- You MUST respond in ROMANIZED/LATIN script only
- DO NOT use Devanagari characters
- Use English letters: a, aa, i, ee, o, oo, k, kh, g, gh, etc.
- Respond in the SAME LANGUAGE (Hindi/Marathi) as user input
- IMPORTANT: Understand that the user is speaking Hindi/Marathi but written in English letters
- Example for Hindi: "Aapko doctor se milna chahiye" NOT "आपको डॉक्टर से मिलना चाहिए"
- Example for Marathi: "Tumhala doctor kade jaave laagel" NOT "तुम्हाला डॉक्टर कडे जावे लागेल"
"""
        
        elif detected_script == 'latin':
            return base_instruction + """
- User has written in LATIN script (English/European languages)
- You MUST respond in LATIN script only
- Use English alphabet: a-z, A-Z
"""
        
        elif detected_script == 'arabic':
            return base_instruction + """
- User has written in ARABIC script
- You MUST respond in ARABIC script only
- Use Arabic characters: ا, ب, ت, ث, etc.
"""
        
        elif detected_script == 'mixed':
            return base_instruction + """
- User has used MIXED scripts
- Respond primarily in the DOMINANT script of user input
- Try to maintain the same script balance as user input
"""
        
        else:
            return base_instruction + """
- Script detection unclear
- Respond in the same language and script style as user input
- DO NOT change the script type
"""

# Global instance
script_detector = ScriptDetector()