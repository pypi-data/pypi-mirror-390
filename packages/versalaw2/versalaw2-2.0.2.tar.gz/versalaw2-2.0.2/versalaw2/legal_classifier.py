# versalaw2/versalaw2/legal_classifier.py
class LegalClassifier:
    def __init__(self):
        self.legal_categories = {
            'hukum_pidana': ['pembunuhan', 'pencurian', 'narkotika', 'korupsi', 'pidana', 'hakim', 'vonis', 'penjara'],
            'hukum_perdata': ['perjanjian', 'kontrak', 'wanprestasi', 'perdata', 'gugatan', 'ganti rugi'],
            'hukum_tata_usaha_negara': ['sengketa', 'administrasi', 'ptun', 'pemerintah', 'negara'],
            'hukum_internasional': ['internasional', 'hukum asing', 'perjanjian internasional', 'bci', 'neural'],
            'hukum_bisnis': ['bisnis', 'perusahaan', 'dagang', 'komersial', 'usaha'],
            'hukum_ketenagakerjaan': ['pekerja', 'karyawan', 'phk', 'tenaga kerja', 'upah'],
            'hukum_keluarga': ['perkawinan', 'cerai', 'waris', 'anak', 'keluarga'],
            'hukum_properti': ['tanah', 'sertifikat', 'hak milik', 'properti', 'bangunan']
        }
        print("✅ LegalClassifier initialized!")
    
    def classify_legal_question(self, question):
        """Classify legal questions into categories"""
        question_lower = question.lower()
        scores = {}
        
        for category, keywords in self.legal_categories.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])
            return {
                'category': best_category[0],
                'confidence': min(best_category[1] / len(self.legal_categories[best_category[0]]), 0.95),
                'matched_keywords': [k for k in self.legal_categories[best_category[0]] 
                                   if k in question_lower],
                'all_categories': scores
            }
        else:
            return {
                'category': 'umum',
                'confidence': 0.3,
                'matched_keywords': [],
                'all_categories': {}
            }
    
    def analyze_legal_issue(self, issue_description):
        """Basic legal issue analysis"""
        classification = self.classify_legal_question(issue_description)
        
        return {
            'issue': issue_description,
            'classification': classification,
            'suggested_actions': self.get_suggested_actions(classification['category']),
            'analysis_timestamp': '2024-01-01',
            'complexity_level': self.assess_complexity(issue_description)
        }
    
    def get_suggested_actions(self, category):
        """Get suggested actions based on legal category"""
        actions = {
            'hukum_pidana': [
                'Konsultasi dengan pengacara pidana',
                'Pelajari KUHP terkait pasal yang dilanggar',
                'Kumpulkan bukti-bukti pendukung',
                'Pahami proses peradilan pidana'
            ],
            'hukum_perdata': [
                'Periksa dokumen perjanjian secara detail',
                'Konsultasi dengan notaris atau pengacara perdata',
                'Siapkan bukti wanprestasi atau kerugian',
                'Pahami tenggat waktu pengajuan gugatan'
            ],
            'hukum_tata_usaha_negara': [
                'Ajukan gugatan ke Pengadilan Tata Usaha Negara (PTUN)',
                'Kumpulkan bukti keputusan administrasi',
                'Konsultasi dengan ahli hukum administrasi',
                'Periksa dasar hukum keputusan yang disengketakan'
            ],
            'hukum_internasional': [
                'Konsultasi dengan ahli hukum internasional',
                'Periksa perjanjian internasional yang berlaku',
                'Identifikasi yurisdiksi yang berwenang',
                'Pelajari konvensi internasional terkait'
            ],
            'hukum_bisnis': [
                'Review kontrak bisnis secara menyeluruh',
                'Konsultasi dengan legal counsel perusahaan',
                'Periksa compliance dengan regulasi bisnis',
                'Siapkan dokumen corporate governance'
            ],
            'hukum_ketenagakerjaan': [
                'Periksa perjanjian kerja dan company regulation',
                'Konsultasi dengan pengacara ketenagakerjaan',
                'Pahami hak dan kewajiban sesuai UU Ketenagakerjaan',
                'Dokumentasikan bukti pelanggaran hubungan kerja'
            ],
            'hukum_keluarga': [
                'Konsultasi dengan pengacara keluarga',
                'Kumpulkan dokumen terkait (akta, sertifikat)',
                'Pahami proses mediasi dan pengadilan agama',
                'Siapkan dokumen pendukung untuk waris atau perceraian'
            ],
            'hukum_properti': [
                'Periksa sertifikat dan dokumen kepemilikan',
                'Konsultasi dengan notaris atau pengacara properti',
                'Verifikasi legalitas dokumen tanah dan bangunan',
                'Pahami peraturan zonasi dan tata ruang'
            ],
            'umum': [
                'Konsultasi dengan pengacara umum untuk assessment awal',
                'Identifikasi UU dan peraturan yang relevan',
                'Kumpulkan semua dokumen dan bukti terkait',
                'Pahami proses hukum yang mungkin dilakukan'
            ]
        }
        return actions.get(category, actions['umum'])
    
    def assess_complexity(self, issue_description):
        """Assess complexity level of legal issue"""
        issue_lower = issue_description.lower()
        complexity_keywords = {
            'high': ['internasional', 'bci', 'neural', 'ghost contract', 'supreme', 'mahkamah agung', 
                    'konstitusi', 'yurisprudensi', 'kasasi', 'peninjauan kembali'],
            'medium': ['gugatan', 'wanprestasi', 'sengketa', 'perdata', 'pidana', 'administrasi'],
            'low': ['konsultasi', 'tanya', 'informasi', 'dasar', 'pengantar']
        }
        
        high_count = sum(1 for keyword in complexity_keywords['high'] if keyword in issue_lower)
        medium_count = sum(1 for keyword in complexity_keywords['medium'] if keyword in issue_lower)
        
        if high_count > 0:
            return 'high'
        elif medium_count > 2:
            return 'medium'
        else:
            return 'low'
    
    def get_legal_references(self, category):
        """Get legal references for specific category"""
        references = {
            'hukum_pidana': ['KUHP (Kitab Undang-Undang Hukum Pidana)', 'KUHAP (Kitab Undang-Undang Hukum Acara Pidana)'],
            'hukum_perdata': ['KUHPer (Kitab Undang-Undang Hukum Perdata)', 'BW (Burgerlijk Wetboek)'],
            'hukum_tata_usaha_negara': ['UU No. 5 Tahun 1986 tentang PTUN', 'UU No. 30 Tahun 2014 tentang Administrasi Pemerintahan'],
            'hukum_internasional': ['Vienna Convention', 'UN Charter', 'International Covenants'],
            'hukum_bisnis': ['UU Perseroan Terbatas', 'UU Perlindungan Konsumen', 'UU Larangan Praktek Monopoli'],
            'hukum_ketenagakerjaan': ['UU No. 13 Tahun 2003 tentang Ketenagakerjaan', 'UU No. 11 Tahun 2020 tentang Cipta Kerja'],
            'hukum_keluarga': ['Kompilasi Hukum Islam', 'UU No. 1 Tahun 1974 tentang Perkawinan'],
            'hukum_properti': ['UU No. 5 Tahun 1960 tentang Agraria', 'UU No. 28 Tahun 2002 tentang Bangunan Gedung']
        }
        return references.get(category, ['Konsultasi dengan ahli hukum terkait'])


class EnhancedLegalClassifier(LegalClassifier):
    def __init__(self):
        super().__init__()
        # Import inside method to avoid circular imports
        from .enhanced_knowledge import EnhancedLegalKnowledge
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
            basic_classification['has_expert_insights'] = True
        else:
            basic_classification['has_expert_insights'] = False
        
        return basic_classification
    
    def analyze_complex_contract(self, contract_text):
        """Analyze complex contracts using ghost contract methodology"""
        contract_lower = contract_text.lower()
        
        # Check for futuristic/tech contracts
        tech_keywords = ['bci', 'neural', 'brain', 'interface', 'digital', 'tech', 'ai', 'artificial intelligence', 'algorithm']
        contract_keywords = ['perjanjian', 'kontrak', 'agreement', 'service', 'license']
        
        is_tech_contract = any(keyword in contract_lower for keyword in tech_keywords)
        is_contract = any(keyword in contract_lower for keyword in contract_keywords)
        
        if is_tech_contract and is_contract:
            ghost_analysis = self.enhanced_knowledge.supreme_cases.get('ghost_contract', {})
            return {
                'analysis_type': 'ghost_contract',
                'validity': 'high_risk_void_analysis',
                'recommendation': 'require_enhanced_safeguards',
                'confidence': 0.88,
                'risk_level': 'high',
                'expert_insights': ghost_analysis.get('preview', 'Analisis kontrak canggih diperlukan')[:300] + "...",
                'suggested_actions': [
                    'Konsultasi dengan ahli hukum teknologi',
                    'Review klausul informed consent',
                    'Verifikasi compliance dengan regulasi data privacy',
                    'Assess liability dan risk allocation'
                ]
            }
        elif is_contract:
            return {
                'analysis_type': 'standard_contract',
                'validity': 'normal_analysis',
                'confidence': 0.75,
                'risk_level': 'medium',
                'suggested_actions': [
                    'Review seluruh klausul kontrak',
                    'Periksa kewajiban dan hak para pihak',
                    'Verifikasi legalitas penandatangan',
                    'Assess konsekuensi wanprestasi'
                ]
            }
        else:
            return {
                'analysis_type': 'unknown',
                'validity': 'cannot_assess',
                'confidence': 0.3,
                'risk_level': 'unknown',
                'suggested_actions': [
                    'Konsultasi dengan pengacara untuk assessment',
                    'Siapkan dokumen lengkap untuk analisis'
                ]
            }
    
    def get_enhanced_suggestions(self, question):
        """Get enhanced suggestions based on expert knowledge"""
        basic_suggestions = self.get_suggested_actions(
            self.classify_legal_question(question)['category']
        )
        
        expert_analysis = self.enhanced_knowledge.get_expert_analysis(question)
        
        if expert_analysis:
            enhanced_suggestions = basic_suggestions + [
                '✅ Gunakan insights dari analisis expert',
                '📚 Review study case terkait dari knowledge base',
                '⚖️ Pertimbangkan pendekatan supreme court level'
            ]
            return enhanced_suggestions
        
        return basic_suggestions
    
    def comprehensive_analysis(self, legal_query):
        """Comprehensive analysis combining all capabilities"""
        classification = self.classify_with_expert_analysis(legal_query)
        complexity = self.assess_complexity(legal_query)
        suggestions = self.get_enhanced_suggestions(legal_query)
        
        # Check if it's a contract analysis request
        is_contract_analysis = any(word in legal_query.lower() for word in 
                                 ['kontrak', 'perjanjian', 'contract', 'agreement'])
        
        contract_analysis = None
        if is_contract_analysis:
            contract_analysis = self.analyze_complex_contract(legal_query)
        
        return {
            'query': legal_query,
            'classification': classification,
            'complexity_assessment': complexity,
            'suggestions': suggestions,
            'contract_analysis': contract_analysis,
            'timestamp': '2024-01-01',
            'analysis_id': f"analysis_{hash(legal_query) % 10000:04d}"
        }
