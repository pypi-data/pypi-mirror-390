"""
PDF processing utilities with real text extraction capabilities.

Supports multiple methods:
1. PyPDF2 for basic text extraction
2. pdfplumber for better layout preservation
3. Mock processing as fallback
"""

import os
import json
import base64
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files and extract content."""
    
    def __init__(self, method: str = "auto"):
        """
        Initialize PDF processor.
        
        Args:
            method: Processing method ('auto', 'pypdf2', 'pdfplumber', 'mock')
        """
        self.method = method
        self._setup_processor()
    
    def _setup_processor(self):
        """Set up the appropriate PDF processing library."""
        self.pypdf2_available = False
        self.pdfplumber_available = False
        
        try:
            import PyPDF2
            self.pypdf2_available = True
            logger.info("PyPDF2 is available for PDF processing")
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        try:
            import pdfplumber
            self.pdfplumber_available = True
            logger.info("pdfplumber is available for PDF processing")
        except ImportError:
            logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted content and metadata
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": f"PDF file not found: {pdf_path}",
                "content": {}
            }
        
        # Choose processing method
        if self.method == "auto":
            if self.pdfplumber_available:
                return self._process_with_pdfplumber(pdf_path)
            elif self.pypdf2_available:
                return self._process_with_pypdf2(pdf_path)
            else:
                return self._mock_process_pdf(pdf_path)
        elif self.method == "pypdf2" and self.pypdf2_available:
            return self._process_with_pypdf2(pdf_path)
        elif self.method == "pdfplumber" and self.pdfplumber_available:
            return self._process_with_pdfplumber(pdf_path)
        else:
            return self._mock_process_pdf(pdf_path)
    
    def _process_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF using PyPDF2."""
        import PyPDF2
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    "title": pdf_reader.metadata.title if pdf_reader.metadata and pdf_reader.metadata.title else os.path.basename(pdf_path),
                    "author": pdf_reader.metadata.author if pdf_reader.metadata and pdf_reader.metadata.author else "Unknown",
                    "subject": pdf_reader.metadata.subject if pdf_reader.metadata and pdf_reader.metadata.subject else "",
                    "pages": len(pdf_reader.pages),
                    "creation_date": str(pdf_reader.metadata.creation_date) if pdf_reader.metadata and pdf_reader.metadata.creation_date else None
                }
                
                # Extract text from all pages
                pages = []
                full_text = []
                
                for i, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    pages.append({
                        "page_number": i + 1,
                        "text": text,
                        "word_count": len(text.split())
                    })
                    full_text.append(text)
                
                return {
                    "success": True,
                    "method": "pypdf2",
                    "content": {
                        "metadata": metadata,
                        "pages": pages,
                        "full_text": "\n\n".join(full_text),
                        "total_words": sum(p["word_count"] for p in pages),
                        "extraction_time": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"PyPDF2 processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": {}
            }
    
    def _process_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF using pdfplumber for better layout preservation."""
        import pdfplumber
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                metadata = {
                    "title": pdf.metadata.get('Title', os.path.basename(pdf_path)),
                    "author": pdf.metadata.get('Author', 'Unknown'),
                    "subject": pdf.metadata.get('Subject', ''),
                    "pages": len(pdf.pages),
                    "creation_date": str(pdf.metadata.get('CreationDate', ''))
                }
                
                # Extract text and tables from all pages
                pages = []
                full_text = []
                all_tables = []
                
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Extract tables
                    tables = page.extract_tables()
                    table_data = []
                    
                    for j, table in enumerate(tables):
                        table_data.append({
                            "table_index": j + 1,
                            "rows": len(table),
                            "data": table
                        })
                    
                    pages.append({
                        "page_number": i + 1,
                        "text": text,
                        "word_count": len(text.split()),
                        "tables": table_data,
                        "table_count": len(tables)
                    })
                    
                    full_text.append(text)
                    all_tables.extend(table_data)
                
                return {
                    "success": True,
                    "method": "pdfplumber",
                    "content": {
                        "metadata": metadata,
                        "pages": pages,
                        "full_text": "\n\n".join(full_text),
                        "total_words": sum(p["word_count"] for p in pages),
                        "total_tables": len(all_tables),
                        "tables": all_tables,
                        "extraction_time": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"pdfplumber processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": {}
            }
    
    def _mock_process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Mock PDF processing for demonstration when no libraries available."""
        filename = os.path.basename(pdf_path)
        
        # Generate realistic mock content
        mock_content = {
            "invoice": {
                "title": "Invoice #12345",
                "pages": [
                    {
                        "page_number": 1,
                        "text": "INVOICE\n\nInvoice Number: 12345\nDate: 2024-01-15\n\nBill To:\nAcme Corporation\n123 Main Street\nAnytown, USA 12345\n\nDescription: Professional Services\nAmount: $5,000.00\n\nTotal Due: $5,000.00",
                        "word_count": 25
                    }
                ],
                "metadata": {
                    "title": "Invoice #12345",
                    "author": "Billing Department",
                    "pages": 1
                }
            },
            "report": {
                "title": "Annual Report 2023",
                "pages": [
                    {
                        "page_number": 1,
                        "text": "ANNUAL REPORT 2023\n\nExecutive Summary\n\nThis year has been marked by significant growth and innovation. Our company has achieved record revenues and expanded into new markets.\n\nKey Highlights:\n- Revenue growth of 25%\n- 3 new product launches\n- Expansion to 5 new countries",
                        "word_count": 45
                    },
                    {
                        "page_number": 2,
                        "text": "Financial Overview\n\nTotal Revenue: $50M\nOperating Expenses: $35M\nNet Profit: $15M\n\nOur financial position remains strong with healthy cash reserves and minimal debt.",
                        "word_count": 25
                    }
                ],
                "metadata": {
                    "title": "Annual Report 2023",
                    "author": "Corporate Communications",
                    "pages": 2
                }
            },
            "default": {
                "title": filename,
                "pages": [
                    {
                        "page_number": 1,
                        "text": f"This is a mock extraction of {filename}.\n\nIn a real implementation, this would contain the actual text extracted from the PDF file.\n\nThe extraction would preserve formatting and structure as much as possible.",
                        "word_count": 30
                    }
                ],
                "metadata": {
                    "title": filename,
                    "author": "Unknown",
                    "pages": 1
                }
            }
        }
        
        # Select appropriate mock based on filename
        content_type = "default"
        for key in mock_content:
            if key in filename.lower():
                content_type = key
                break
        
        mock_data = mock_content[content_type]
        
        return {
            "success": True,
            "method": "mock",
            "content": {
                "metadata": mock_data["metadata"],
                "pages": mock_data["pages"],
                "full_text": "\n\n".join(p["text"] for p in mock_data["pages"]),
                "total_words": sum(p["word_count"] for p in mock_data["pages"]),
                "extraction_time": datetime.now().isoformat(),
                "note": "This is mock data. Install PyPDF2 or pdfplumber for real PDF processing."
            }
        }
    
    def extract_images(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract images from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted images with metadata
        """
        if self.pypdf2_available:
            return self._extract_images_pypdf2(pdf_path)
        else:
            return self._mock_extract_images(pdf_path)
    
    def _extract_images_pypdf2(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract images using PyPDF2."""
        import PyPDF2
        
        images = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/XObject' in page['/Resources']:
                        xObject = page['/Resources']['/XObject'].get_object()
                        
                        for obj in xObject:
                            if xObject[obj]['/Subtype'] == '/Image':
                                images.append({
                                    "page": page_num + 1,
                                    "name": obj,
                                    "width": xObject[obj]['/Width'],
                                    "height": xObject[obj]['/Height'],
                                    "type": xObject[obj].get('/Filter', 'Unknown')
                                })
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
        
        return images
    
    def _mock_extract_images(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Mock image extraction."""
        return [
            {
                "page": 1,
                "name": "logo.png",
                "width": 200,
                "height": 100,
                "type": "PNG"
            },
            {
                "page": 2,
                "name": "chart.jpg",
                "width": 600,
                "height": 400,
                "type": "JPEG"
            }
        ]
    
    def search_text(self, pdf_path: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for text within PDF.
        
        Args:
            pdf_path: Path to PDF file
            query: Search query
            
        Returns:
            List of matches with page numbers and context
        """
        # First extract all text
        result = self.process_pdf(pdf_path)
        
        if not result["success"]:
            return []
        
        matches = []
        query_lower = query.lower()
        
        for page in result["content"]["pages"]:
            text = page["text"]
            text_lower = text.lower()
            
            # Find all occurrences
            start = 0
            while True:
                pos = text_lower.find(query_lower, start)
                if pos == -1:
                    break
                
                # Extract context (50 chars before and after)
                context_start = max(0, pos - 50)
                context_end = min(len(text), pos + len(query) + 50)
                context = text[context_start:context_end]
                
                # Add ellipsis if truncated
                if context_start > 0:
                    context = "..." + context
                if context_end < len(text):
                    context = context + "..."
                
                matches.append({
                    "page": page["page_number"],
                    "position": pos,
                    "context": context,
                    "query": query
                })
                
                start = pos + 1
        
        return matches


def process_pdf_batch(pdf_paths: List[str], method: str = "auto") -> List[Dict[str, Any]]:
    """
    Process multiple PDF files.
    
    Args:
        pdf_paths: List of PDF file paths
        method: Processing method
        
    Returns:
        List of processing results
    """
    processor = PDFProcessor(method=method)
    results = []
    
    for pdf_path in pdf_paths:
        result = processor.process_pdf(pdf_path)
        result["file_path"] = pdf_path
        results.append(result)
        
        if result["success"]:
            logger.info(f"Successfully processed {pdf_path}")
        else:
            logger.error(f"Failed to process {pdf_path}: {result.get('error')}")
    
    return results


def analyze_pdf_content(pdf_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze extracted PDF content.
    
    Args:
        pdf_result: Result from process_pdf
        
    Returns:
        Analysis including statistics and insights
    """
    if not pdf_result.get("success"):
        return {"error": "PDF processing failed"}
    
    content = pdf_result["content"]
    full_text = content.get("full_text", "")
    
    # Basic statistics
    stats = {
        "total_pages": len(content.get("pages", [])),
        "total_words": content.get("total_words", 0),
        "total_characters": len(full_text),
        "avg_words_per_page": content.get("total_words", 0) / max(1, len(content.get("pages", [])))
    }
    
    # Content analysis
    analysis = {
        "statistics": stats,
        "has_tables": content.get("total_tables", 0) > 0,
        "table_count": content.get("total_tables", 0),
        "extraction_method": pdf_result.get("method", "unknown"),
        "metadata": content.get("metadata", {})
    }
    
    # Simple keyword extraction (most common words)
    if full_text:
        words = full_text.lower().split()
        word_freq = {}
        
        # Count word frequency
        for word in words:
            # Skip short words and common stopwords
            if len(word) > 4 and word not in ['the', 'and', 'for', 'that', 'this', 'with', 'from']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["top_keywords"] = [{"word": word, "count": count} for word, count in top_keywords]
    
    return analysis


if __name__ == "__main__":
    # Test PDF processing
    logging.basicConfig(level=logging.INFO)
    
    # Create a test processor
    processor = PDFProcessor()
    
    print("PDF Processor Test")
    print("=" * 50)
    print(f"PyPDF2 available: {processor.pypdf2_available}")
    print(f"pdfplumber available: {processor.pdfplumber_available}")
    
    # Test with a mock file
    test_file = "test_invoice.pdf"
    print(f"\nProcessing mock file: {test_file}")
    
    result = processor.process_pdf(test_file)
    
    if result["success"]:
        print(f"\nExtraction method: {result['method']}")
        print(f"Total pages: {len(result['content']['pages'])}")
        print(f"Total words: {result['content']['total_words']}")
        print(f"\nFirst 200 characters of text:")
        print(result['content']['full_text'][:200] + "...")
        
        # Test search
        print("\nSearching for 'Invoice'...")
        matches = processor.search_text(test_file, "Invoice")
        print(f"Found {len(matches)} matches")
        
        # Test analysis
        print("\nAnalyzing content...")
        analysis = analyze_pdf_content(result)
        print(f"Analysis: {json.dumps(analysis, indent=2)}")
    else:
        print(f"Processing failed: {result.get('error')}")