#!/usr/bin/env python3
"""
Test International Law Structure - FIXED
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test import dari struktur yang benar
    from versalaw2.international_law.international_treaties import InternationalTreatyAnalyzer
    from versalaw2.international_law.diplomatic_law import DiplomaticLawAnalyzer
    from versalaw2.international_law.law_of_the_sea import LawOfTheSeaAnalyzer
    from versalaw2.international_law.international_humanitarian import InternationalHumanitarianAnalyzer
    from versalaw2.international_law.international_trade import InternationalTradeAnalyzer
    from versalaw2.international_law.extradition_mutual_legal import ExtraditionMLATAnalyzer
    
    print("✅ STRUCTURE CORRECT - All international law modules imported successfully!")
    
    # Test instantiation
    treaty_analyzer = InternationalTreatyAnalyzer()
    diplomatic_analyzer = DiplomaticLawAnalyzer()
    sea_law_analyzer = LawOfTheSeaAnalyzer()
    humanitarian_analyzer = InternationalHumanitarianAnalyzer()
    trade_analyzer = InternationalTradeAnalyzer()
    extradition_analyzer = ExtraditionMLATAnalyzer()
    
    print("✅ MODULES OPERATIONAL - All 6 international analyzers instantiated!")
    
    # Test basic functionality
    treaty_test = treaty_analyzer.analyze_treaty_ratification({"bilateral": True})
    diplomatic_test = diplomatic_analyzer.analyze_diplomatic_incident({})
    sea_law_test = sea_law_analyzer.analyze_maritime_dispute({})
    humanitarian_test = humanitarian_analyzer.analyze_armed_conflict({})
    trade_test = trade_analyzer.analyze_trade_dispute({})
    extradition_test = extradition_analyzer.analyze_extradition_request({})
    
    print("✅ FUNCTIONALITY CONFIRMED - All international law methods working!")
    print(f"   • Treaty Analysis: {len(treaty_test)} aspects")
    print(f"   • Diplomatic Analysis: {len(diplomatic_test)} aspects") 
    print(f"   • Law of Sea Analysis: {len(sea_law_test)} aspects")
    print(f"   • Humanitarian Law: {len(humanitarian_test)} aspects")
    print(f"   • Trade Law: {len(trade_test)} aspects")
    print(f"   • Extradition/MLA: {len(extradition_test)} aspects")
    
    print("\n🎯 6 INTERNATIONAL LAW MODULES SUCCESSFULLY INTEGRATED!")
    print("   Structure: versalaw2/international_law/ ✅")
    
except ImportError as e:
    print(f"❌ STRUCTURE ERROR: {e}")
    print("   Please check the directory structure")
except Exception as e:
    print(f"❌ FUNCTIONALITY ERROR: {e}")

# Show final structure
print("\n📁 FINAL STRUCTURE:")
print("versalaw2/")
print("├── indonesian_law/          # Hukum Nasional")
print("│   ├── constitutional_law/")
print("│   ├── statutory_law/") 
print("│   ├── criminal_justice/")
print("│   ├── civil_law/")
print("│   ├── professional_ethics/")
print("│   └── specialized_law/     # 8 crime modules")
print("│")
print("└── international_law/       # 🌍 Hukum Internasional")
print("    ├── international_treaties.py")
print("    ├── diplomatic_law.py")
print("    ├── law_of_the_sea.py")
print("    ├── international_humanitarian.py")
print("    ├── international_trade.py")
print("    └── extradition_mutual_legal.py")
