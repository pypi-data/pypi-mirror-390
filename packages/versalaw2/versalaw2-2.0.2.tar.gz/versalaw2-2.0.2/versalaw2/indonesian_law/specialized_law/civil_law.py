# versalaw2/indonesian_law/specialized_law/civil_law.py
"""
Civil Law Analysis Module
Analisis berdasarkan KUH Perdata dan hukum perdata Indonesia
"""

class CivilLawAnalyzer:
    """Analyzer for civil law compliance"""
    
    def __init__(self):
        self.civil_code_db = self._load_civil_code_database()
        self.contract_law_db = self._load_contract_law_database()
    
    def analyze_civil_issues(self, text, context=None):
        """Analyze civil law issues"""
        analysis = {
            "civil_code_references": [],
            "contract_law_issues": [],
            "property_law_issues": [],
            "family_law_issues": [],
            "obligation_issues": []
        }
        
        # Check civil code references
        civil_refs = self._check_civil_code_references(text)
        analysis["civil_code_references"].extend(civil_refs)
        
        # Check contract law issues
        contract_issues = self._check_contract_law_issues(text)
        analysis["contract_law_issues"].extend(contract_issues)
        
        # Check property law issues
        property_issues = self._check_property_law_issues(text)
        analysis["property_law_issues"].extend(property_issues)
        
        return analysis
    
    def _check_civil_code_references(self, text):
        """Check references to civil code provisions"""
        references = []
        text_lower = text.lower()
        
        civil_code_articles = {
            "1338 kuhperdata": "Asas kebebasan berkontrak",
            "1320 kuhperdata": "Syarat sahnya perjanjian",
            "1233 kuhperdata": "Sumber perikatan",
            "1365 kuhperdata": "Perbuatan melawan hukum",
            "1545 kuhperdata": "Jual beli"
        }
        
        for article, description in civil_code_articles.items():
            if article in text_lower:
                references.append({
                    "article": article,
                    "description": description,
                    "type": "civil_code_reference"
                })
        
        return references
    
    def _check_contract_law_issues(self, text):
        """Check contract law issues"""
        issues = []
        text_lower = text.lower()
        
        contract_issues = {
            "wanprestasi": "Keterlambatan atau tidak dipenuhinya kewajiban",
            "force majeure": "Keadaan memaksa",
            "cacat tersembunyi": "Cacat tersembunyi dalam jual beli",
            "pembatalan sepihak": "Pembatalan perjanjian sepihak"
        }
        
        for issue, description in contract_issues.items():
            if issue in text_lower:
                issues.append({
                    "issue": issue,
                    "description": description,
                    "relevance": "contract_law",
                    "severity": "medium"
                })
        
        return issues
    
    def _check_property_law_issues(self, text):
        """Check property law issues"""
        issues = []
        text_lower = text.lower()
        
        property_keywords = {
            "sertifikat hak milik": "Bukti kepemilikan properti",
            "hak guna bangunan": "HGB - Hak Guna Bangunan",
            "hak pakai": "Hak Pakai atas tanah",
            "hipotek": "Hak tanggungan atas properti",
            "gadai": "Jaminan kebendaan"
        }
        
        for keyword, description in property_keywords.items():
            if keyword in text_lower:
                issues.append({
                    "property_issue": keyword,
                    "description": description,
                    "type": "property_law"
                })
        
        return issues
    
    def _load_civil_code_database(self):
        """Load civil code database"""
        return {
            "buku_1": "Orang",
            "buku_2": "Benda", 
            "buku_3": "Perikatan",
            "buku_4": "Pembuktian dan Kadaluarsa"
        }
    
    def _load_contract_law_database(self):
        """Load contract law database"""
        return {
            "prinsip_umum": [
                "Asas kebebasan berkontrak",
                "Asas pacta sunt servanda",
                "Asas itikad baik"
            ],
            "jenis_perjanjian": [
                "Jual beli", "Sewa menyewa", "Perjanjian kerja",
                "Perjanjian utang piutang", "Perjanjian bagi hasil"
            ]
        }
