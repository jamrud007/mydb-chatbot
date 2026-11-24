"""
Prompt Templates for LLM
"""
from config import Config


def _dialect_rules(engine: str) -> str:
    """Return SQL dialect rules for the selected engine."""
    if engine == 'oracle':
        return """### Date/Time Helpers (Oracle):
- Monthly grouping: TO_CHAR(CAST(col AS TIMESTAMP), 'YYYY-MM')
- Year: EXTRACT(YEAR FROM CAST(col AS TIMESTAMP))
- Today: TRUNC(SYSDATE)"""

    return """### SQL DIALECT RULES (MySQL):
- Use MySQL SQL syntax.
- Use `LIMIT n` for row limiting.
- Date examples:
  - Monthly grouping: `DATE_FORMAT(date_col, '%Y-%m')`
  - Year: `YEAR(date_col)`."""


# Template for converting natural language to SQL
NL_TO_SQL_TEMPLATE = """You are an Oracle SQL expert for a container terminal gate OCR system.

### System Context:
- GATE_TRANSACTIONS: main transaction log. STATUS values: 'ocr_completed', 'ocr_corrected', 'ocr_inprogess'. Links to OCR data via TRANSACTION_OCR_DATA_ID.
- GATES: list of physical gates (TYPE: 'IN' or 'OUT', ACTIVE: 1=active).
- GATE_DEVICES: cameras/devices at each gate (GATE_ID → GATES.ID).
- GATE_ACTION_TIMES: timestamps of each action per transaction (GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID).
- OCR_DATAS: raw OCR scan results (container number, ISO code, axle count, seal, chassis, etc.).
- TRANSACTION_OCR_DATAS: OCR data finalized per transaction (same columns as OCR_DATAS plus PLAT_NO, STATUS).
- OCR_AUTOGATE_ACCURACY: accuracy scores per transaction (GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID).
- ETICKETS: container e-tickets (CONTAINER_ID, EXPORT_OR_IMPORT, VESSEL_CODE, VOYAGE_CODE, etc.).
- USERS: system users (USERNAME, ROLE, ACTIVE).

### Schema (use ONLY these exact names):
{schema}

### Oracle SQL Rules (STRICT):
1. NEVER use TOP N — use FETCH FIRST N ROWS ONLY at end of query.
2. NEVER use LIMIT — Oracle only.
3. Always CAST timestamp columns: CAST(TIME_CREATED AS TIMESTAMP).
4. String comparison is case-sensitive — use exact case from schema comments.
5. Use only table/column names listed in schema above. Never invent names.
6. Output valid JSON only — no markdown, no extra text.

{dialect_rules}

### Output Format (JSON only):
{{
  "suggested_queries": [
    {{
      "sql": "SELECT ... FROM ... WHERE ... ORDER BY ... FETCH FIRST 30 ROWS ONLY",
      "explanation": "Penjelasan singkat dalam Bahasa Indonesia"
    }}
  ]
}}

### Question: {query}
### Context: {context}"""


# Template for converting SQL results to natural language
SQL_TO_NL_TEMPLATE = """You are a data analyst assistant. Convert the following SQL query results into a natural, easy-to-understand response.

Original User Question: {question}

SQL Query Executed:
{query}

Query Results:
{results}

Number of rows: {row_count}

Guidelines:
1. Provide a clear, conversational summary of the results.
2. Highlight key insights or interesting patterns.
3. If no results were found, explain why and suggest alternatives.
4. Use the same language as the user's question (Indonesian or English).
5. Keep it concise but informative.
6. Include specific numbers and data points from the results.

Provide your response in plain text (not JSON)."""


# Template for error explanation
ERROR_EXPLANATION_TEMPLATE = """You are a helpful database assistant. A user asked a question but encountered an error.

User Question: {question}

Error Message: {error}

Guidelines:
1. Explain what went wrong in simple, non-technical terms.
2. Suggest how the user can rephrase their question.
3. Provide 2-3 example questions they could ask instead.
4. Use the same language as the user's question (Indonesian or English).
5. Be encouraging and helpful.

Provide your response in plain text (not JSON)."""


# Template for follow-up suggestions
FOLLOWUP_TEMPLATE = """Based on the following conversation, suggest 3 relevant follow-up questions the user might want to ask.

Recent conversation:
{conversation_history}

Database Schema (for context):
{schema}

Guidelines:
1. Suggest specific, actionable questions.
2. Build on what was already discussed.
3. Use the same language as the conversation (Indonesian or English).
4. Questions should be diverse (different aspects of the data).

Respond with JSON format:
{{
  "suggestions": [
    "Question 1",
    "Question 2",
    "Question 3"
  ]
}}"""


def format_nl_to_sql_prompt(user_query, schema, conversation_context=""):
    """
    Format the NL to SQL prompt

    Args:
        user_query: User's natural language question
        schema: Formatted database schema
        conversation_context: Previous conversation context

    Returns:
        str: Formatted prompt
    """
    engine = getattr(Config, 'DB_ENGINE', 'mysql').lower()
    return NL_TO_SQL_TEMPLATE.format(
        query=user_query,
        schema=schema,
        context=conversation_context or "No previous context",
        dialect_rules=_dialect_rules(engine)
    )


def format_sql_to_nl_prompt(user_question, sql_query, results, row_count):
    """
    Format the SQL results to NL prompt

    Args:
        user_question: Original user question
        sql_query: SQL query that was executed
        results: Query results (as formatted string)
        row_count: Number of rows returned

    Returns:
        str: Formatted prompt
    """
    return SQL_TO_NL_TEMPLATE.format(
        question=user_question,
        query=sql_query,
        results=results,
        row_count=row_count
    )


def format_error_explanation_prompt(user_question, error_message):
    """
    Format the error explanation prompt

    Args:
        user_question: User's question that caused error
        error_message: Error message to explain

    Returns:
        str: Formatted prompt
    """
    return ERROR_EXPLANATION_TEMPLATE.format(
        question=user_question,
        error=error_message
    )


def format_followup_prompt(conversation_history, schema):
    """
    Format the follow-up suggestions prompt

    Args:
        conversation_history: Recent conversation as string
        schema: Database schema for context

    Returns:
        str: Formatted prompt
    """
    return FOLLOWUP_TEMPLATE.format(
        conversation_history=conversation_history,
        schema=schema
    )


# Template for data analysis
DATA_ANALYSIS_TEMPLATE = """You are a Data Analyst expert. Analyze the following query results and provide a brief, insightful summary.

User Question: {question}

Columns: {columns}
Data (Top 20 rows):
{data}

Instructions:
1. Provide a "Mini Analysis" in Indonesian.
2. Focus on trends, outliers, or dominant categories.
3. Be concise (max 3 bullets).
4. Do NOT verify the SQL, just analyze the numbers.
5. Example: "Kategori Health memiliki revenue 2x lipat dari kategori lainnya."

Output ONLY the analysis text."""


def format_data_analysis_prompt(question, columns, data):
    """
    Format the data analysis prompt

    Args:
        question: User's original question
        columns: List of column names
        data: Sample data rows

    Returns:
        str: Formatted prompt
    """
    return DATA_ANALYSIS_TEMPLATE.format(question=question, columns=columns, data=data)
