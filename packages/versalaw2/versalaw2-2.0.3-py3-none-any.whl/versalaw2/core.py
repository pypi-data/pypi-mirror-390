import re
from typing import Dict, List

# CLASS RENAMED: LegalAnalyzer -> VERSALAW2
class VERSALAW2:
    def __init__(self):
        self.risk_keywords = {
            'high': [
                'denda 100%', 'sanksi', 'terminasi', 'ganti rugi',
                'wanprestasi', 'jaminan tanah', 'sita', 'denda 50%'
            ],
            'medium': [
                'penalty', 'jaminan', 'collateral', 'denda',
                'confidentiality', 'indemnity', 'late payment'
            ],
            'low': [
                'perpanjangan', 'renewal', 'notice', 'pemberitahuan',
                'review', 'amandement'
            ]
        }
    
    def analyze_contract(self, text: str) -> Dict:
        if not text or not text.strip():
            return self._empty_result("Empty contract text provided")
        
        risk_factors, risk_score = self._assess_risk(text)
        risk_level = self._determine_risk_level(risk_score)
        jurisdiction = self._detect_jurisdiction(text)
        issues = self._detect_issues(text, risk_factors)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "jurisdiction": jurisdiction,
            "issues": issues,
            "risk_factors": risk_factors,
            "clauses": extract_clauses(text)
        }
    
    def _assess_risk(self, text: str) -> tuple:
        risk_factors = []
        score = 0
        
        for level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    risk_factors.append(f"{keyword} ({level} risk)")
                    if level == 'high':
                        score += 3
                    elif level == 'medium':
                        score += 2
                    else:
                        score += 1
        
        return risk_factors, score
    
    def _determine_risk_level(self, score: int) -> str:
        if score >= 10:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
    
    def _detect_jurisdiction(self, text: str) -> str:
        text_lower = text.lower()
        if 'indonesia' in text_lower or 'jakarta' in text_lower:
            return "Indonesia"
        elif 'singapore' in text_lower:
            return "Singapore"
        else:
            return "Unknown"
    
    def _detect_issues(self, text: str, risk_factors: List[str]) -> List[str]:
        issues = []
        if len(risk_factors) > 5:
            issues.append("High number of risk factors detected")
        if 'denda 100%' in text.lower():
            issues.append("Extremely high penalty clause detected")
        if 'jaminan tanah' in text.lower():
            issues.append("Land collateral requires careful review")
        return issues
    
    def _empty_result(self, message: str) -> Dict:
        return {
            "risk_level": "unknown",
            "risk_score": 0,
            "jurisdiction": "unknown",
            "issues": [message],
            "risk_factors": [],
            "clauses": []
        }

# Keep existing functions for backward compatibility
def analyze_contract(text: str) -> Dict:
    analyzer = VERSALAW2()
    return analyzer.analyze_contract(text)

def extract_clauses(text: str):
    clauses = re.findall(r'PASAL \d+[^\n]*', text, re.IGNORECASE)
    return clauses or ["No formal clauses detected"]
