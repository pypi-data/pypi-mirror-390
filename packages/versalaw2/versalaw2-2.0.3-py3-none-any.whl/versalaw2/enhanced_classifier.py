# versalaw2/versalaw2/enhanced_classifier.py
from .legal_classifier import LegalClassifier
from .enhanced_knowledge import EnhancedLegalKnowledge

class EnhancedLegalClassifier(LegalClassifier):
    def __init__(self):
        super().__init__()
        self.enhanced_knowledge = EnhancedLegalKnowledge()
        print("🚀 Enhanced Legal Classifier initialized!")
    
    def classify_with_expert_analysis(self, question):
        """Enhanced classification with expert knowledge"""
        basic_classification = self.classify_legal_question(question)
        
        # Get expert analysis if available
        expert_analysis = self.enhanced_knowledge.get_expert_analysis(question)
        
        if expert_analysis:
            basic_classification['expert_analysis'] = expert_analysis
            basic_classification['confidence'] = min(basic_classification.get('confidence', 0.7) + 0.15, 0.95)
            basic_classification['analysis_level'] = expert_analysis['type']
            basic_classification['source'] = 'enhanced_knowledge_base'
        
        return basic_classification
    
    def analyze_complex_contract(self, contract_text):
        """Analyze complex contracts using ghost contract methodology"""
        contract_lower = contract_text.lower()
        
        if any(keyword in contract_lower for keyword in ['bci', 'neural', 'brain', 'interface', 'digital', 'tech']):
            ghost_analysis = self.enhanced_knowledge.supreme_cases.get('ghost_contract', {})
            return {
                'analysis_type': 'ghost_contract',
                'validity': 'high_risk_void_analysis',
                'recommendation': 'require_enhanced_safeguards',
                'confidence': 0.88,
                'expert_insights': ghost_analysis.get('preview', '')[:500] + "..."
            }
        
        return {
            'analysis_type': 'standard_contract', 
            'validity': 'normal_analysis',
            'confidence': 0.75
        }
