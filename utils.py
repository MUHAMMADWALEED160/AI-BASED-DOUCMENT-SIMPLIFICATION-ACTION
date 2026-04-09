import os
import random

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    """Check if the filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_document(filename, file_data):
    """
    Simulate an AI document processing system.
    In a real application, this would pass the binary file_data to an ML model or API.
    """
    summaries = [
        "This document appears to be a financial report. Recommendation: Review Q3 projections.",
        "Contains technical specifications. Recommendation: Forward to the engineering team.",
        "General correspondence detected. Recommendation: Archive for records.",
        "Identified as a contract or legal agreement. Recommendation: Requires signature from legal.",
        "Looks like graphical or image content. Recommendation: Add relevant meta tags.",
        "Unclassified text document. Recommendation: No immediate action required."
    ]
    
    size_kb = len(file_data) / 1024
    summary = random.choice(summaries)
    detailed_summary = f"[AI Analysis] File '{filename}' ({size_kb:.1f} KB) processed. {summary}"
    
    return detailed_summary