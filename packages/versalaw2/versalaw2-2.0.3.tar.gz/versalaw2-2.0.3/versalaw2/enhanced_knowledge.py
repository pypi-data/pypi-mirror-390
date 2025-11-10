# versalaw2/versalaw2/enhanced_knowledge.py
import os
from pathlib import Path

class EnhancedLegalKnowledge:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.advanced_cases = self.load_advanced_cases()
        self.law_library = self.load_law_library()
        self.supreme_cases = self.load_supreme_cases()
        print(f"✅ Enhanced knowledge loaded: {len(self.advanced_cases.get('advanced_questions', []))} advanced cases, "
              f"{len(self.law_library)} law libraries, {len(self.supreme_cases)} supreme cases")
    
    def load_advanced_cases(self):
        """Load 20 advanced legal questions"""
        cases = {}
        advanced_path = self.base_path / "legal_knowledge" / "advanced_cases"
        
        try:
            # Load main advanced questions file
            main_file = advanced_path / "ADVANCED_LEGAL_QUESTIONS_20.md"
            if main_file.exists():
                content = main_file.read_text(encoding='utf-8')
                cases['advanced_questions'] = self.parse_advanced_questions(content)
                print(f"📚 Loaded advanced questions: {len(cases['advanced_questions'])} questions")
        except Exception as e:
            print(f"❌ Error loading advanced cases: {e}")
        
        return cases
    
    def load_law_library(self):
        """Load law library batches"""
        library = {}
        library_path = self.base_path / "legal_knowledge" / "law_library"
        
        try:
            for file in library_path.glob("*.md"):
                if file.exists():
                    content = file.read_text(encoding='utf-8')
                    # SIMPLE VERSION - just store content preview
                    library[file.stem] = {
                        'content_preview': content[:500] + "..." if len(content) > 500 else content,
                        'line_count': len(content.split('\n')),
                        'file_size': len(content),
                        'file_name': file.name
                    }
                    print(f"📖 Loaded law library: {file.name}")
        except Exception as e:
            print(f"❌ Error loading law library: {e}")
        
        return library
    
    def load_supreme_cases(self):
        """Load supreme court level cases"""
        supreme_cases = {}
        supreme_path = self.base_path / "legal_knowledge" / "supreme_analysis"
        
        try:
            # Load ghost contract analysis
            ghost_file = supreme_path / "GHOST_CONTRACT_COMPLETE.md"
            if ghost_file.exists():
                content = ghost_file.read_text(encoding='utf-8')
                supreme_cases['ghost_contract'] = {
                    'type': 'supreme_analysis',
                    'title': 'Ghost Contract - BCI Neural Interface',
                    'preview': content[:1000] + "..." if len(content) > 1000 else content,
                    'achievement': 'Supreme Court Level Analysis Completed',
                    'file_source': 'GHOST_CONTRACT_COMPLETE.md'
                }
                print(f"👻 Loaded ghost contract analysis")
            
            # Load supreme law cases
            supreme_file = supreme_path / "SUPREME_LAW_CASES_COMPLETE.md"
            if supreme_file.exists():
                content = supreme_file.read_text(encoding='utf-8')
                supreme_cases['supreme_cases'] = {
                    'type': 'supreme_court',
                    'title': 'Supreme Law Cases Complete',
                    'preview': content[:1000] + "..." if len(content) > 1000 else content,
                    'file_source': 'SUPREME_LAW_CASES_COMPLETE.md'
                }
                print(f"🏛️ Loaded supreme court cases")
                
        except Exception as e:
            print(f"❌ Error loading supreme cases: {e}")
        
        return supreme_cases
    
    def parse_advanced_questions(self, content):
        """Parse advanced legal questions structure"""
        questions = []
        lines = content.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## PERTANYAAN'):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    'title': line,
                    'content': [],
                    'analysis': [],
                    'domain': 'unknown'
                }
            elif line.startswith('### JAWABAN:') or 'Analisis Hukum' in line:
                if current_question:
                    current_question['analysis'].append(line)
            elif current_question:
                if 'BIDANG:' in line:
                    current_question['domain'] = line.replace('#', '').replace('⚖️', '').strip()
                else:
                    current_question['content'].append(line)
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def get_expert_analysis(self, question):
        """Get expert-level analysis for a legal question"""
        question_lower = question.lower()
        
        # Search in advanced cases
        advanced_questions = self.advanced_cases.get('advanced_questions', [])
        for case in advanced_questions:
            case_text = ' '.join(case.get('content', [])).lower()
            if any(keyword in question_lower for keyword in ['bawah minimum', 'minimum', 'pidana bawah']):
                if 'bawah' in case_text or 'minimum' in case_text:
                    return {
                        'type': 'advanced_analysis',
                        'source': 'ADVANCED_LEGAL_QUESTIONS_20.md',
                        'case': case,
                        'confidence': 0.9
                    }
        
        # Search for ghost contract topics
        if any(keyword in question_lower for keyword in ['ghost', 'bci', 'neural', 'brain', 'interface', 'digital contract']):
            ghost_contract = self.supreme_cases.get('ghost_contract')
            if ghost_contract:
                return {
                    'type': 'supreme_analysis',
                    'source': 'GHOST_CONTRACT_COMPLETE.md', 
                    'case': ghost_contract,
                    'confidence': 0.95
                }
        
        # Search for supreme court topics
        if any(keyword in question_lower for keyword in ['supreme', 'mahkamah agung', 'kasasi', 'peninjauan kembali']):
            supreme_case = self.supreme_cases.get('supreme_cases')
            if supreme_case:
                return {
                    'type': 'supreme_court',
                    'source': 'SUPREME_LAW_CASES_COMPLETE.md',
                    'case': supreme_case,
                    'confidence': 0.85
                }
        
        return None
    
    def get_available_domains(self):
        """Get list of available legal domains in enhanced knowledge"""
        domains = set()
        advanced_questions = self.advanced_cases.get('advanced_questions', [])
        
        for case in advanced_questions:
            domain = case.get('domain', 'unknown')
            if domain and domain != 'unknown':
                domains.add(domain)
        
        return list(domains)
