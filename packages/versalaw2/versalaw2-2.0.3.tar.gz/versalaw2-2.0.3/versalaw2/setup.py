# versalaw2/examples/advanced_features_demo.py
from versalaw2 import EnhancedLegalClassifier

def demo_advanced_features():
    print("🚀 VERSALAW2 ENHANCED FEATURES DEMO")
    print("=" * 50)
    
    classifier = EnhancedLegalClassifier()
    
    # Test 1: Advanced Legal Questions
    print("\n1. 🔥 ADVANCED LEGAL QUESTION ANALYSIS")
    question = "Apakah hakim boleh menjatuhkan pidana di bawah minimum?"
    result = classifier.classify_with_expert_analysis(question)
    print(f"Question: {question}")
    print(f"Expert Analysis: {'Available' if 'expert_analysis' in result else 'Standard'}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    
    # Test 2: Ghost Contract Analysis
    print("\n2. 👻 GHOST CONTRACT ANALYSIS")
    contract = "BCI neural interface agreement with digital consent"
    analysis = classifier.analyze_complex_contract(contract)
    print(f"Contract: {contract}")
    print(f"Analysis Type: {analysis['analysis_type']}")
    print(f"Validity Assessment: {analysis['validity']}")
    
    # Test 3: Supreme Court Level Reasoning
    print("\n3. 🏛️ SUPREME COURT LEVEL REASONING")
    complex_case = "International BCI contract dispute with product liability"
    supreme_analysis = classifier.classify_with_expert_analysis(complex_case)
    print(f"Case: {complex_case}")
    print(f"Analysis Level: {supreme_analysis.get('source', 'basic')}")
    print(f"Confidence Score: {supreme_analysis.get('confidence', 0):.2f}")

if __name__ == "__main__":
    demo_advanced_features()
