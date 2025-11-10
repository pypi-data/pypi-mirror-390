# versalaw2/advanced_features_demo.py
import sys
import os

# Add parent directory to path to import local version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from versalaw2.enhanced_classifier import EnhancedLegalClassifier
    from versalaw2.enhanced_knowledge import EnhancedLegalKnowledge
    print("✅ Successfully imported enhanced features from local development!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def demo_advanced_features():
    print("🚀 VERSALAW2 ENHANCED FEATURES DEMO")
    print("=" * 60)
    
    # Initialize classifier
    print("Initializing Enhanced Legal Classifier...")
    classifier = EnhancedLegalClassifier()
    
    # Test 1: Advanced Legal Questions
    print("\n1. 🔥 ADVANCED LEGAL QUESTION ANALYSIS")
    questions = [
        "Apakah hakim boleh menjatuhkan pidana di bawah minimum?",
        "Bagaimana analisis kontrak BCI neural interface?",
        "Apa yang dimaksud dengan ghost contract?",
        "Standard contract for employment"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   {i}. Question: {question}")
        result = classifier.classify_with_expert_analysis(question)
        print(f"      Analysis Level: {result.get('analysis_level', 'basic')}")
        print(f"      Confidence: {result.get('confidence', 0):.2f}")
        print(f"      Source: {result.get('source', 'standard')}")
        if 'expert_analysis' in result:
            expert = result['expert_analysis']
            print(f"      ✅ Expert Analysis: {expert['type']} (confidence: {expert.get('confidence', 0):.2f})")
    
    # Test 2: Ghost Contract Analysis
    print("\n2. 👻 GHOST CONTRACT ANALYSIS")
    contracts = [
        "BCI neural interface agreement with digital consent",
        "Standard employment contract for software developer",
        "Digital neural link service agreement"
    ]
    
    for i, contract in enumerate(contracts, 1):
        print(f"\n   {i}. Contract: {contract}")
        analysis = classifier.analyze_complex_contract(contract)
        print(f"      Analysis Type: {analysis['analysis_type']}")
        print(f"      Validity: {analysis['validity']}")
        print(f"      Confidence: {analysis['confidence']:.2f}")
        if analysis['analysis_type'] == 'ghost_contract':
            print(f"      💡 Insights: {analysis['expert_insights'][:100]}...")
    
    # Test 3: Available Domains
    print("\n3. 📚 AVAILABLE ENHANCED KNOWLEDGE DOMAINS")
    domains = classifier.enhanced_knowledge.get_available_domains()
    for domain in domains:
        if domain != 'unknown' and domain:
            print(f"   📖 {domain}")
    
    print(f"\n🎉 DEMO COMPLETED! Enhanced knowledge base activated!")

if __name__ == "__main__":
    demo_advanced_features()
