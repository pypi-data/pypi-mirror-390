# versalaw2/versalaw2/__init__.py
from .legal_classifier import LegalClassifier, EnhancedLegalClassifier

try:
    from .enhanced_knowledge import EnhancedLegalKnowledge
    __all__ = ['LegalClassifier', 'EnhancedLegalClassifier', 'EnhancedLegalKnowledge']
    print("✅ Enhanced features loaded successfully!")
    
except ImportError as e:
    print(f"⚠️  Enhanced features not available: {e}")
    __all__ = ['LegalClassifier', 'EnhancedLegalClassifier']
