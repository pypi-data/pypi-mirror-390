#!/usr/bin/env python3
"""
Test Script for Indonesian Law Modules
"""
import sys
sys.path.insert(0, '.')

from versalaw2.indonesian_law import IndonesianLawAnalyzer
from versalaw2.indonesian_law.hierarchy.constitutional_law import ConstitutionalLawAnalyzer
from versalaw2.indonesian_law.hierarchy.statutory_law import StatutoryLawAnalyzer

def main():
    print("🇮🇩 TEST MODUL HUKUM INDONESIA")
    print("=" * 50)
    
    # Test Constitutional Law
    print("\n1. 🏛️ TEST CONSTITUTIONAL LAW ANALYZER")
    const_analyzer = ConstitutionalLawAnalyzer()
    
    test_text_1 = "Perjanjian ini membatasi kebebasan berserikat dan berpendapat"
    result_1 = const_analyzer.analyze_compliance(test_text_1)
    
    print("   Sample:", test_text_1)
    print("   Rights violations:", len(result_1["rights_violations"]))
    if result_1["rights_violations"]:
        for violation in result_1["rights_violations"]:
            print(f"     - {violation['right']}: {violation['issue']}")
    
    # Test Statutory Law
    print("\n2. 📚 TEST STATUTORY LAW ANALYZER")
    stat_analyzer = StatutoryLawAnalyzer()
    
    test_text_2 = "Peraturan Daerah ini menyimpangi UU No. 12 Tahun 2011"
    result_2 = stat_analyzer.analyze_compliance(test_text_2)
    
    print("   Sample:", test_text_2)
    print("   Hierarchy issues:", len(result_2["hierarchy_issues"]))
    if result_2["hierarchy_issues"]:
        for issue in result_2["hierarchy_issues"]:
            print(f"     - {issue['issue']}")
    
    # Test Integrated Analysis
    print("\n3. 🔄 TEST INTEGRATED INDONESIAN LAW ANALYZER")
    indo_analyzer = IndonesianLawAnalyzer()
    
    test_text_3 = """
    PERATURAN DAERAH TENTANG KETERTIBAN UMUM
    Pasal 1: Peraturan ini dibuat berdasarkan UU No. 12 Tahun 2011
    Pasal 2: Dilarang melakukan kegiatan yang membatasi hak kebebasan berpendapat
    Pasal 3: Peraturan ini menyimpangi ketentuan dalam UU No. 8 Tahun 1999
    """
    
    result_3 = indo_analyzer.comprehensive_analysis(test_text_3)
    
    print("   Comprehensive analysis completed!")
    print("   Constitutional compliance:", result_3["compliance_summary"]["constitutional_compliance"])
    print("   Statutory compliance:", result_3["compliance_summary"]["statutory_compliance"])
    print("   Overall risk:", result_3["compliance_summary"]["overall_risk"])
    
    print("\n4. 💡 RECOMMENDATIONS:")
    for rec in result_3["recommendations"]:
        print(f"   [{rec['priority'].upper()}] {rec['message']}")
    
    print("\n🎉 TEST MODUL HUKUM INDONESIA BERHASIL!")

if __name__ == "__main__":
    main()
