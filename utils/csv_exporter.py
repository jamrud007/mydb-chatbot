"""
CSV Exporter - Convert query results to CSV format
"""
import csv
import io
from typing import List, Dict, Any
from fastapi import Response
import logging

logger = logging.getLogger(__name__)


class CSVExporter:
    """Helper class to export query results as CSV"""
    
    @classmethod
    def results_to_csv(cls, results: List[Dict[str, Any]], columns: List[str]) -> str:
        """
        Convert query results to CSV string
        
        Args:
            results: List of row dictionaries
            columns: List of column names
        
        Returns:
            CSV formatted string with UTF-8 BOM
        """
        if not results or not columns:
            return ""
        
        # Create string buffer
        output = io.StringIO()
        
        # Write UTF-8 BOM for Excel compatibility
        output.write('\ufeff')
        
        # Create CSV writer
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            quoting=csv.QUOTE_NONNUMERIC,
            lineterminator='\n'
        )
        
        # Write header
        writer.writeheader()
        
        # Write rows
        for row in results:
            # Convert None to empty string
            cleaned_row = {k: (v if v is not None else '') for k, v in row.items()}
            writer.writerow(cleaned_row)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    @classmethod
    def generate_csv_response(
        cls, 
        results: List[Dict[str, Any]], 
        columns: List[str],
        filename: str = 'query_results.csv'
    ) -> Response:
        """
        Generate FastAPI response for CSV download
        
        Args:
            results: List of row dictionaries
            columns: List of column names
            filename: Name for downloaded file
        
        Returns:
            FastAPI Response object with CSV content
        """
        csv_content = cls.results_to_csv(results, columns)
        
        # Create response
        response = Response(
            content=csv_content,
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
        
        return response
    
    @classmethod
    def estimate_csv_size(cls, results: List[Dict[str, Any]], columns: List[str]) -> int:
        """
        Estimate CSV file size in bytes
        
        Args:
            results: List of row dictionaries
            columns: List of column names
        
        Returns:
            Estimated size in bytes
        """
        if not results or not columns:
            return 0
        
        # Estimate: header + average row size * number of rows
        header_size = len(','.join(columns)) + 1  # +1 for newline
        
        # Sample first row for average estimation
        sample_row = results[0]
        row_size = sum(len(str(v)) if v is not None else 0 for v in sample_row.values())
        row_size += len(columns) - 1  # Commas
        row_size += 1  # Newline
        
        total_size = header_size + (row_size * len(results))
        
        return total_size
