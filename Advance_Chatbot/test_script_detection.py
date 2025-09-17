#!/usr/bin/env python3
# Script Detection Test

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from script_detector import script_detector

def test_script_detection():
    test_cases = [
        # Devanagari Hindi
        ("मेरा सिर दर्द कर रहा है", "devanagari_hindi"),
        ("मुझे बुखार है", "devanagari_hindi"),
        
        # Devanagari Marathi
        ("माझे डोके दुखत आहे", "devanagari_marathi"), 
        ("मला ताप आला आहे", "devanagari_marathi"),
        
        # Romanized Hindi
        ("mera sir dard kar raha hai", "romanized_hindi"),
        ("mujhe bukhar hai", "romanized_hindi"),
        ("kaise ho aap", "romanized_hindi"),
        ("kya hal hai", "romanized_hindi"),
        ("main theek hoon", "romanized_hindi"),
        
        # Romanized Marathi
        ("mala taap aala aahe", "romanized_marathi"),
        ("majhe doke dukhata aahe", "romanized_marathi"),
        ("kasa aahe tu", "romanized_marathi"),
        ("mi bara aahe", "romanized_marathi"),
        ("tumhala kay pahije", "romanized_marathi"),
        ("tyala nako te", "romanized_marathi"),
        
        # Pure Latin/English
        ("Hello, how are you?", "latin"),
        ("I have a headache", "latin"),
        ("What is the weather like?", "latin"),
        
        # Mixed cases
        ("मैं ठीक हूं but feeling tired", "mixed"),
        
        # Arabic
        ("مرحبا كيف حالك", "arabic"),
    ]
    
    print("=== Script Detection Test ===\n")
    
    for text, expected in test_cases:
        detected = script_detector.detect_script(text)
        status = "✅ PASS" if detected == expected else "❌ FAIL"
        
        print(f"Text: {text}")
        print(f"Expected: {expected}")
        print(f"Detected: {detected}")
        print(f"Status: {status}")
        print("-" * 50)
        
        # Show the instruction that would be generated
        instruction = script_detector.create_script_instruction(detected, text)
        print(f"Generated Instruction Preview:")
        print(instruction[:150] + "..." if len(instruction) > 150 else instruction)
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_script_detection()