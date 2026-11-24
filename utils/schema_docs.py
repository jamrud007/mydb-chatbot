"""
Schema Documentation Generator
Auto-generates beautiful documentation from database schema
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SchemaDocGenerator:
    """
    Generates documentation from database schema
    Supports Markdown, HTML, and JSON formats
    """
    
    def __init__(self, schema_manager, db_connection=None):
        """
        Initialize documentation generator
        
        Args:
            schema_manager: SchemaManager instance
            db_connection: DatabaseConnection for statistics (optional)
        """
        self.schema_manager = schema_manager
        self.db_connection = db_connection
        logger.info("SchemaDocGenerator initialized")
    
    def generate_markdown(self, include_stats: bool = False) -> str:
        """
        Generate Markdown documentation
        
        Args:
            include_stats: Include table row counts (requires db_connection)
        
        Returns:
            str: Markdown documentation
        """
        schema = self.schema_manager.get_schema()
        lines = []
        
        # Header
        lines.append("# Database Schema Documentation")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Tables:** {len(schema['tables'])}")
        lines.append("")
        
        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        for i, table in enumerate(schema['tables'], 1):
            lines.append(f"{i}. [{table['name']}](#{table['name'].lower()})")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Table Details
        for table in schema['tables']:
            table_name = table['name']
            columns = table['columns']
            
            lines.append(f"## {table_name}")
            lines.append("")
            
            # Table info
            lines.append(f"**Total Columns:** {len(columns)}")
            
            # Get row count if available
            if include_stats and self.db_connection:
                try:
                    _, rows = self.db_connection.execute_query(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = rows[0][0] if rows else 0
                    lines.append(f"**Total Rows:** {row_count:,}")
                except Exception as e:
                    logger.warning(f"Could not get row count for {table_name}: {e}")
            
            lines.append("")
            
            # Columns table
            lines.append("### Columns")
            lines.append("")
            lines.append("| Column | Type | Nullable | Key | Default | Extra |")
            lines.append("|--------|------|----------|-----|---------|-------|")
            
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                nullable = '✓' if col.get('nullable', True) else '✗'
                key = col.get('key', '-')
                default = col.get('default', '-') or '-'
                extra = col.get('extra', '-') or '-'
                
                lines.append(f"| `{col_name}` | {col_type} | {nullable} | {key} | {default} | {extra} |")
            
            lines.append("")
            
            # Primary Keys
            primary_keys = [col['name'] for col in columns if col.get('key') == 'PRI']
            if primary_keys:
                lines.append("**Primary Key(s):** " + ", ".join(f"`{pk}`" for pk in primary_keys))
                lines.append("")
            
            # Foreign Keys (if available)
            foreign_keys = [col for col in columns if col.get('key') == 'MUL']
            if foreign_keys:
                lines.append("**Foreign Key(s):** " + ", ".join(f"`{fk['name']}`" for fk in foreign_keys))
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_html(self, include_stats: bool = False) -> str:
        """
        Generate HTML documentation
        
        Args:
            include_stats: Include table row counts
        
        Returns:
            str: HTML documentation
        """
        schema = self.schema_manager.get_schema()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Schema Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            background: #ecf0f1;
            padding: 10px;
            border-left: 4px solid #3498db;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        code {{
            background: #e8f4f8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .toc {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        .toc li {{
            padding: 5px 0;
        }}
        .toc a {{
            color: #3498db;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge.primary {{
            background: #e74c3c;
            color: white;
        }}
        .badge.foreign {{
            background: #f39c12;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>📚 Database Schema Documentation</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p class="meta">Total Tables: {len(schema['tables'])}</p>
    
    <div class="toc">
        <h2>📑 Table of Contents</h2>
        <ul>
"""
        
        # Table of Contents
        for table in schema['tables']:
            html += f'            <li><a href="#{table["name"]}">{table["name"]}</a></li>\n'
        
        html += """        </ul>
    </div>
"""
        
        # Table Details
        for table in schema['tables']:
            table_name = table['name']
            columns = table['columns']
            
            html += f'\n    <h2 id="{table_name}">🗂️ {table_name}</h2>\n'
            html += f'    <p><strong>Total Columns:</strong> {len(columns)}</p>\n'
            
            # Get row count
            if include_stats and self.db_connection:
                try:
                    _, rows = self.db_connection.execute_query(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = rows[0][0] if rows else 0
                    html += f'    <p><strong>Total Rows:</strong> {row_count:,}</p>\n'
                except:
                    pass
            
            html += '    <table>\n'
            html += '        <thead>\n'
            html += '            <tr>\n'
            html += '                <th>Column</th>\n'
            html += '                <th>Type</th>\n'
            html += '                <th>Nullable</th>\n'
            html += '                <th>Key</th>\n'
            html += '                <th>Default</th>\n'
            html += '                <th>Extra</th>\n'
            html += '            </tr>\n'
            html += '        </thead>\n'
            html += '        <tbody>\n'
            
            for col in columns:
                key_badge = ''
                if col.get('key') == 'PRI':
                    key_badge = '<span class="badge primary">PRIMARY</span>'
                elif col.get('key') == 'MUL':
                    key_badge = '<span class="badge foreign">FOREIGN</span>'
                else:
                    key_badge = col.get('key', '-')
                
                html += '            <tr>\n'
                html += f'                <td><code>{col["name"]}</code></td>\n'
                html += f'                <td>{col["type"]}</td>\n'
                html += f'                <td>{"✓" if col.get("nullable", True) else "✗"}</td>\n'
                html += f'                <td>{key_badge}</td>\n'
                html += f'                <td>{col.get("default", "-") or "-"}</td>\n'
                html += f'                <td>{col.get("extra", "-") or "-"}</td>\n'
                html += '            </tr>\n'
            
            html += '        </tbody>\n'
            html += '    </table>\n'
        
        html += """
</body>
</html>
"""
        
        return html
    
    def generate_json(self, include_stats: bool = False) -> str:
        """
        Generate JSON documentation
        
        Args:
            include_stats: Include table row counts
        
        Returns:
            str: JSON documentation
        """
        schema = self.schema_manager.get_schema()
        
        doc = {
            'generated_at': datetime.now().isoformat(),
            'total_tables': len(schema['tables']),
            'tables': []
        }
        
        for table in schema['tables']:
            table_doc = {
                'name': table['name'],
                'total_columns': len(table['columns']),
                'columns': table['columns']
            }
            
            # Add row count
            if include_stats and self.db_connection:
                try:
                    _, rows = self.db_connection.execute_query(f"SELECT COUNT(*) FROM {table['name']}")
                    table_doc['total_rows'] = rows[0][0] if rows else 0
                except:
                    table_doc['total_rows'] = None
            
            # Extract primary keys
            table_doc['primary_keys'] = [col['name'] for col in table['columns'] if col.get('key') == 'PRI']
            
            # Extract foreign keys
            table_doc['foreign_keys'] = [col['name'] for col in table['columns'] if col.get('key') == 'MUL']
            
            doc['tables'].append(table_doc)
        
        return json.dumps(doc, indent=2, default=str)
