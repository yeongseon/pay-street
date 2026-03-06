"""Prompt templates for PayStreet AI content generation."""

SCRIPT_GENERATION_PROMPT = """\
You are generating a simulated interview script based only on structured salary data.
This is not a real interview.
Use the following data:
- job_title: {job_title}
- experience_years: {experience_years}
- region: {region}
- company_size: {company_size}
- salary_range: {salary_range}
- tone: {tone}
Requirements:
- Return only valid JSON
- Keep it under 40 seconds when spoken
- Use interviewer/interviewee format
- Do not invent facts beyond the given data
- Express salary as a range, not a single exact value
- Output format:
{{
  "hook": "<one sentence hook question>",
  "dialogue": [
    {{"speaker": "interviewer", "line": "<question>"}},
    {{"speaker": "interviewee", "line": "<answer>"}}
  ],
  "outro": "<call to action>"
}}
"""

SCRIPT_GENERATION_PROMPT_VERSION = "v1.0"

TOPIC_TITLE_TEMPLATES = [
    "{experience}년차 {job_title} 연봉 얼마예요",
    "{region} {job_title} 연봉 현실",
    "{job_title} {experience}년차 연봉 범위",
    "{job_title} vs {job_title_2} 연봉 비교",
]


def build_script_prompt(
    job_title: str,
    experience_years: int,
    region: str,
    company_size: str,
    salary_range: str,
    tone: str = "casual",
) -> str:
    """Build the script generation prompt with provided salary data."""
    return SCRIPT_GENERATION_PROMPT.format(
        job_title=job_title,
        experience_years=experience_years,
        region=region,
        company_size=company_size,
        salary_range=salary_range,
        tone=tone,
    )
