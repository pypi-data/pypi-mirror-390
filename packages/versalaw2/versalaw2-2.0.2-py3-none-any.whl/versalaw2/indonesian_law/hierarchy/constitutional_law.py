# versalaw2/indonesian_law/hierarchy/constitutional_law.py
"""
Constitutional Law Analysis Module
Analisis berdasarkan UUD 1945 dan TAP MPR
"""

class ConstitutionalLawAnalyzer:
    """Analyzer for constitutional law compliance"""
    
    def __init__(self):
        self.constitutional_framework = self._load_constitutional_framework()
        self.fundamental_rights = self._load_fundamental_rights()
    
    def analyze_compliance(self, legal_text):
        """Analyze compliance with constitutional framework"""
        analysis = {
            "constitutional_issues": [],
            "rights_violations": [],
            "hierarchy_violations": [],
            "constitutional_references": []
        }
        
        # Check UUD 1945 compliance
        uud_issues = self._check_uud_compliance(legal_text)
        analysis["constitutional_issues"].extend(uud_issues)
        
        # Check fundamental rights
        rights_issues = self._check_fundamental_rights(legal_text)
        analysis["rights_violations"].extend(rights_issues)
        
        # Check constitutional references
        references = self._detect_constitutional_references(legal_text)
        analysis["constitutional_references"].extend(references)
        
        return analysis
    
    def _check_uud_compliance(self, text):
        """Check compliance with UUD 1945"""
        issues = []
        text_lower = text.lower()
        
        # Basic constitutional principles
        constitutional_principles = {
            "negara hukum": "Prinsip negara hukum (Rechtsstaat)",
            "demokrasi": "Prinsip demokrasi",
            "hak asasi manusia": "Prinsip hak asasi manusia", 
            "kesejahteraan sosial": "Prinsip kesejahteraan sosial",
            "keadilan sosial": "Prinsip keadilan sosial"
        }
        
        for principle, description in constitutional_principles.items():
            if principle in text_lower:
                issues.append({
                    "type": "constitutional_principle",
                    "principle": principle,
                    "description": description,
                    "compliance": "referenced"
                })
        
        return issues
    
    def _check_fundamental_rights(self, text):
        """Check for fundamental rights violations"""
        violations = []
        text_lower = text.lower()
        
        fundamental_rights = {
            "kebebasan berserikat": "Pasal 28E UUD 1945",
            "kebebasan berkumpul": "Pasal 28E UUD 1945",
            "kebebasan berpendapat": "Pasal 28E UUD 1945",
            "hak atas pekerjaan": "Pasal 27 UUD 1945",
            "hak atas penghidupan layak": "Pasal 27 UUD 1945",
            "hak atas pendidikan": "Pasal 31 UUD 1945",
            "hak beragama": "Pasal 29 UUD 1945"
        }
        
        # Check for potential restrictions on fundamental rights
        restrictive_keywords = ["dilarang", "tidak boleh", "dikenakan sanksi", "dibatasi"]
        
        for right, article in fundamental_rights.items():
            if right in text_lower:
                for restriction in restrictive_keywords:
                    if restriction in text_lower:
                        violations.append({
                            "right": right,
                            "article": article,
                            "issue": f"Potensi pembatasan {right}",
                            "severity": "medium"
                        })
        
        return violations
    
    def _detect_constitutional_references(self, text):
        """Detect references to constitutional provisions"""
        references = []
        text_lower = text.lower()
        
        constitutional_references = {
            "uud 1945": "Konstitusi Republik Indonesia",
            "tap mpr": "Ketetapan Majelis Permusyawaratan Rakyat",
            "amandemen uud": "Perubahan UUD 1945"
        }
        
        for ref, description in constitutional_references.items():
            if ref in text_lower:
                references.append({
                    "reference": ref,
                    "description": description,
                    "type": "constitutional"
                })
        
        return references
    
    def _load_constitutional_framework(self):
        """Load constitutional framework database"""
        return {
            "uud_1945": {
                "pembukaan": "Pembukaan UUD 1945",
                "batang_tubuh": "Batang Tubuh UUD 1945",
                "amandemen": ["I", "II", "III", "IV"]
            },
            "tap_mpr": {
                "tap_mpr_x_1998": "Penyelenggaraan Negara yang Bersih dan Bebas KKN",
                "tap_mpr_iii_2000": "Sumber Hukum dan Tata Urutan Peraturan"
            }
        }
    
    def _load_fundamental_rights(self):
        """Load fundamental rights database"""
        return {
            "hak_sipil": [
                "hak hidup", "hak kebebasan", "hak kesetaraan"
            ],
            "hak_ekonomi": [
                "hak pekerjaan", "hak berusaha", "hak milik"
            ],
            "hak_sosial": [
                "hak pendidikan", "hak kesehatan", "hak perumahan"
            ]
        }
