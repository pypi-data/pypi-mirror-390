# versalaw2/simple_test.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simple_test():
    print("🧪 SIMPLE ENHANCED FEATURES TEST")
    print("=" * 50)
    
    try:
        from versalaw2.enhanced_knowledge import EnhancedLegalKnowledge
        
        # Test knowledge loading
        print("1. Testing Enhanced Knowledge Loading...")
        knowledge = EnhancedLegalKnowledge()
        
        print(f"   ✅ Advanced Cases: {len(knowledge.advanced_cases.get('advanced_questions', []))} questions")
        print(f"   ✅ Law Libraries: {len(knowledge.law_library)} files") 
        print(f"   ✅ Supreme Cases: {len(knowledge.supreme_cases)} analyses")
        
        # Test expert analysis
        print("\n2. Testing Expert Analysis...")
        test_question = "hakim menjatuhkan pidana di bawah minimum"
        analysis = knowledge.get_expert_analysis(test_question)
        
        if analysis:
            print(f"   ✅ Expert analysis found: {analysis['type']}")
            print(f"   ✅ Source: {analysis['source']}")
            print(f"   ✅ Confidence: {analysis.get('confidence', 0):.2f}")
        else:
            print("   ⚠️  No expert analysis found for this question")
            
        # Test ghost contract
        print("\n3. Testing Ghost Contract Detection...")
        ghost_question = "BCI neural interface contract validity"
        ghost_analysis = knowledge.get_expert_analysis(ghost_question)
        
        if ghost_analysis:
            print(f"   ✅ Ghost contract analysis found!")
            print(f"   ✅ Type: {ghost_analysis['type']}")
        else:
            print("   ⚠️  No ghost contract analysis found")
        
        print("\n🎉 SIMPLE TEST COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
