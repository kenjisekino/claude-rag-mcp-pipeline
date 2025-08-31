import os
import PyPDF2
from docx import Document
import json

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.txt', '.pdf', '.docx', '.md']
    
    def extract_text(self, file_path):
        """Extract text from various file formats"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt' or ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        
        elif ext == '.docx':
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        return ""
    
    def semantic_chunk_llm(self, text, max_chunk_size=800, min_chunk_size=100):
        """Split text at sentence boundaries while preserving semantic coherence"""
        if not text.strip():
            return []
        
        # Split into sentences (handling common abbreviations)
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed max_chunk_size
            if current_length + sentence_length > max_chunk_size and current_chunk:
                # Save current chunk if it meets minimum size
                chunk_text = ' '.join(current_chunk).strip()
                if len(chunk_text) >= min_chunk_size:
                    chunks.append(chunk_text)
                
                # Start new chunk with current sentence
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_length += sentence_length + 1  # +1 for space
        
        # Add final chunk if it exists and meets minimum size
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            if len(chunk_text) >= min_chunk_size:
                chunks.append(chunk_text)
            elif chunks:
                # If final chunk is too small, merge with previous chunk
                chunks[-1] += ' ' + chunk_text
        
        return chunks
    
    def _split_into_sentences(self, text):
        """Split text into sentences, handling common abbreviations"""
        # Common abbreviations that shouldn't trigger sentence splits
        abbreviations = {'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Inc.', 'Corp.', 'Ltd.', 'Co.', 
                        'vs.', 'etc.', 'i.e.', 'e.g.', 'U.S.', 'U.K.', 'Ph.D.', 'M.D.'}
        
        # Simple sentence splitting (can be improved with more sophisticated NLP)
        sentences = []
        current_sentence = ""
        
        words = text.split()
        
        for i, word in enumerate(words):
            current_sentence += word + " "
            
            # Check if word ends with sentence-ending punctuation
            if word.endswith(('.', '!', '?')):
                # Check if it's not an abbreviation
                if word not in abbreviations:
                    # Look ahead to see if next word starts with capital (likely new sentence)
                    if i + 1 < len(words) and (words[i + 1][0].isupper() if words[i + 1] else False):
                        sentences.append(current_sentence.strip())
                        current_sentence = ""
                    # If it's end of text, add the sentence
                    elif i + 1 >= len(words):
                        sentences.append(current_sentence.strip())
                        current_sentence = ""
        
        # Add any remaining text as final sentence
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Legacy method maintained for backwards compatibility"""
        return self.semantic_chunk_llm(text, max_chunk_size=800)
    
    def process_directory(self, directory_path):
        """Process all documents in a directory"""
        all_chunks = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_formats):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file}")
                    
                    text = self.extract_text(file_path)
                    if text.strip():  # Only process non-empty files
                        # Use semantic chunking
                        chunks = self.semantic_chunk_llm(text)
                        
                        # Add metadata to each chunk
                        for i, chunk in enumerate(chunks):
                            all_chunks.append({
                                'text': chunk,
                                'source': file,
                                'chunk_id': f"{file}_{i}",
                                'file_path': file_path
                            })
        
        return all_chunks