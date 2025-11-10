# versalaw2/indonesian_law/hierarchy/statutory_law.py
"""
Statutory Law Analysis Module
Analisis berdasarkan UU, PERPU, dan hierarki peraturan
"""

class StatutoryLawAnalyzer:
    """Analyzer for statutory law compliance"""
    
    def __init__(self):
        self.legal_hierarchy = self._load_legal_hierarchy()
        self.statutory_database = self._load_statutory_database()
    
    def analyze_compliance(self, legal_text):
        """Analyze compliance with statutory framework"""
        analysis = {
            "hierarchy_issues": [],
            "statutory_references": [],
            "conflict_analysis": [],
            "compliance_level": "unknown"
        }
        
        # Check legal hierarchy
        hierarchy_issues = self._check_legal_hierarchy(legal_text)
        analysis["hierarchy_issues"].extend(hierarchy_issues)
        
        # Detect statutory references
        references = self._detect_statutory_references(legal_text)
        analysis["statutory_references"].extend(references)
        
        # Analyze potential conflicts
        conflicts = self._analyze_potential_conflicts(legal_text)
        analysis["conflict_analysis"].extend(conflicts)
        
        return analysis
    
    def _check_legal_hierarchy(self, text):
        """Check compliance with legal hierarchy"""
        issues = []
        text_lower = text.lower()
        
        hierarchy_rules = {
            "perda": ["uu", "perpu", "pp", "perpres"],
            "perpres": ["uu", "perpu", "pp"],
            "pp": ["uu", "perpu"],
            "perpu": ["uu"]
        }
        
        for lower_reg, higher_regs in hierarchy_rules.items():
            if lower_reg in text_lower:
                # Check if lower regulation tries to override higher one
                for higher_reg in higher_regs:
                    if f"menyimpangi {higher_reg}" in text_lower or f"bertentangan dengan {higher_reg}" in text_lower:
                        issues.append({
                            "type": "hierarchy_violation",
                            "lower_regulation": lower_reg,
                            "higher_regulation": higher_reg,
                            "issue": f"{lower_reg.upper()} tidak boleh menyimpangi {higher_reg.upper()}",
                            "severity": "high"
                        })
        
        return issues
    
    def _detect_statutory_references(self, text):
        """Detect references to statutory laws"""
        references = []
        text_lower = text.lower()
        
        statutory_patterns = {
            r"uu\s+no\.?\s*(\d+)\s*\/\s*(\d{4})": "Undang-Undang",
            r"perpu\s+no\.?\s*(\d+)\s*\/\s*(\d{4})": "Peraturan Pemerintah Pengganti Undang-Undang",
            r"pp\s+no\.?\s*(\d+)\s*\/\s*(\d{4})": "Peraturan Pemerintah",
            r"perpres\s+no\.?\s*(\d+)\s*\/\s*(\d{4})": "Peraturan Presiden"
        }
        
        import re
        for pattern, law_type in statutory_patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                references.append({
                    "type": law_type,
                    "reference": match.group(0),
                    "number": match.group(1),
                    "year": match.group(2)
                })
        
        return references
    
    def _analyze_potential_conflicts(self, text):
        """Analyze potential conflicts with existing laws"""
        conflicts = []
        text_lower = text.lower()
        
        # Common legal conflicts to check
        conflict_areas = {
            "kepailitan": ["uu no. 37 tahun 2004", "hukum dagang"],
            "perlindungan konsumen": ["uu no. 8 tahun 1999", "hak konsumen"],
            "persaingan usaha": ["uu no. 5 tahun 1999", "monopoli"],
            "perlindungan data pribadi": ["uu no. 27 tahun 2022", "privasi"]
        }
        
        for area, related_laws in conflict_areas.items():
            if area in text_lower:
                conflicts.append({
                    "area": area,
                    "related_laws": related_laws,
                    "check_required": True
                })
        
        return conflicts
    
    def _load_legal_hierarchy(self):
        """Load Indonesian legal hierarchy"""
        return {
            "level_1": ["UUD 1945", "TAP MPR"],
            "level_2": ["Undang-Undang", "PERPU"],
            "level_3": ["Peraturan Pemerintah"],
            "level_4": ["Peraturan Presiden"],
            "level_5": ["Peraturan Daerah", "Peraturan Menteri"]
        }
    
    def _load_statutory_database(self):
        """Load statutory laws database"""
        return {
            "uu_dasar": [
                "UU No. 12 Tahun 2011 - Pembentukan Peraturan Perundang-undangan",
                "UU No. 15 Tahun 2019 - Perubahan atas UU No. 12 Tahun 2011"
            ],
            "uu_pidana": [
                "KUHP - Kitab Undang-Undang Hukum Pidana",
                "KUHAP - Kitab Undang-Undang Hukum Acara Pidana"
            ],
            "uu_perdata": [
                "KUHPerdata - Kitab Undang-Undang Hukum Perdata",
                "KUHD - Kitab Undang-Undang Hukum Dagang"
            ]
        }
