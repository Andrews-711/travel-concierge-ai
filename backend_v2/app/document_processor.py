"""
Document processing utilities
Extract text from PDF, DOCX, TXT and chunk for RAG
"""
import io
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX bytes"""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting DOCX: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT bytes"""
    try:
        return file_content.decode('utf-8').strip()
    except:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            raise ValueError(f"Error extracting TXT: {str(e)}")


def extract_text(filename: str, file_content: bytes) -> str:
    """
    Extract text from file based on extension
    
    Args:
        filename: Name of the file
        file_content: File bytes
    
    Returns:
        Extracted text
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_content)
    elif ext == 'txt':
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # At least 50% of chunk
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if len(c) > 50]  # Filter tiny chunks


def process_document(filename: str, file_content: bytes) -> Dict[str, Any]:
    """
    Process document: extract text and chunk
    
    Args:
        filename: Name of file
        file_content: File bytes
    
    Returns:
        Dict with text, chunks, and metadata
    """
    # Extract text
    text = extract_text(filename, file_content)
    
    # Chunk text
    chunks = chunk_text(text)
    
    # Create metadata for each chunk
    metadatas = [
        {
            'filename': filename,
            'chunk_index': i,
            'total_chunks': len(chunks)
        }
        for i in range(len(chunks))
    ]
    
    return {
        'filename': filename,
        'full_text': text,
        'chunks': chunks,
        'metadatas': metadatas,
        'num_chunks': len(chunks)
    }
