"""
Resume-Job Matching Workflow - Real-World Example

A comprehensive, production-ready workflow that analyzes resumes against job descriptions,
providing detailed match analysis and recommendations.
"""

import sys
import logging
from typing import Dict, Any, List

# Add the utils directory to path
sys.path.insert(0, '.')

from kaygraph import Graph, ValidatedNode
from utils import call_llm, extract_json
from nodes import ConceptNode, MapperNode, ConditionalNode, ConfigurableBatchNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumeParserNode(ValidatedNode):
    """Parses resume text into structured data."""

    def __init__(self):
        super().__init__(node_id="resume_parser", max_retries=2)

    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("resume_text", "")

    def exec(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume."""
        prompt = f"""
        Extract the following information from this resume text:

        {resume_text}

        Return JSON with these fields:
        - name: Full name
        - experience_years: Total years of experience (number)
        - skills: List of technical skills
        - education: Highest degree and field
        - previous_companies: List of previous companies
        - achievements: Key achievements (max 3)

        If any field cannot be found, use null.
        """

        try:
            result = extract_json(
                prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "experience_years": {"type": "number"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "education": {"type": "string"},
                        "previous_companies": {"type": "array", "items": {"type": "string"}},
                        "achievements": {"type": "array", "items": {"type": "string"}}
                    }
                }
            )
            return result
        except Exception as e:
            self.logger.error(f"Resume parsing failed: {e}")
            return {
                "name": "Unknown",
                "experience_years": 0,
                "skills": [],
                "education": None,
                "previous_companies": [],
                "achievements": []
            }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["resume_data"] = exec_res
        return "parse_job"


class JobParserNode(ValidatedNode):
    """Parses job description into structured data."""

    def __init__(self):
        super().__init__(node_id="job_parser", max_retries=2)

    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("job_text", "")

    def exec(self, job_text: str) -> Dict[str, Any]:
        """Extract structured information from job description."""
        prompt = f"""
        Extract the following information from this job description:

        {job_text}

        Return JSON with these fields:
        - title: Job title
        - required_experience: Required years of experience (number)
        - required_skills: List of required technical skills
        - preferred_skills: List of preferred/bonus skills
        - responsibilities: Key responsibilities (max 4)
        - company_type: Company type (startup, mid_size, enterprise, etc.)
        - industry: Industry sector
        - salary_range: Salary range if mentioned
        - remote_work: Whether remote work is offered (true/false)

        If any field cannot be found, use null.
        """

        try:
            result = extract_json(
                prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "required_experience": {"type": "number"},
                        "required_skills": {"type": "array", "items": {"type": "string"}},
                        "preferred_skills": {"type": "array", "items": {"type": "string"}},
                        "responsibilities": {"type": "array", "items": {"type": "string"}},
                        "company_type": {"type": "string"},
                        "industry": {"type": "string"},
                        "salary_range": {"type": "string"},
                        "remote_work": {"type": "boolean"}
                    }
                }
            )
            return result
        except Exception as e:
            self.logger.error(f"Job parsing failed: {e}")
            return {
                "title": "Unknown Position",
                "required_experience": 0,
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "company_type": None,
                "industry": None,
                "salary_range": None,
                "remote_work": False
            }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["job_data"] = exec_res
        return "analyze_match"


class MatchAnalyzerNode(ValidatedNode):
    """Analyzes compatibility between resume and job."""

    def __init__(self):
        super().__init__(node_id="match_analyzer", max_retries=1)

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "resume": shared.get("resume_data", {}),
            "job": shared.get("job_data", {})
        }

    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed compatibility analysis."""
        resume = data["resume"]
        job = data["job"]

        # Calculate skill matches
        resume_skills = set(skill.lower() for skill in resume.get("skills", []))
        required_skills = set(skill.lower() for skill in job.get("required_skills", []))
        preferred_skills = set(skill.lower() for skill in job.get("preferred_skills", []))

        required_matches = resume_skills & required_skills
        preferred_matches = resume_skills & preferred_skills
        missing_required = required_skills - resume_skills

        # Calculate experience match
        resume_experience = resume.get("experience_years", 0)
        required_experience = job.get("required_experience", 0)
        experience_score = min(1.0, resume_experience / max(required_experience, 1))

        # Use LLM for qualitative analysis
        analysis_prompt = f"""
        Analyze the match between this candidate and job:

        RESUME:
        Name: {resume.get('name')}
        Experience: {resume.get('experience_years')} years
        Skills: {', '.join(resume.get('skills', []))}
        Education: {resume.get('education')}
        Previous Companies: {', '.join(resume.get('previous_companies', []))}
        Key Achievements: {', '.join(resume.get('achievements', []))}

        JOB:
        Title: {job.get('title')}
        Required Experience: {job.get('required_experience')} years
        Required Skills: {', '.join(job.get('required_skills', []))}
        Preferred Skills: {', '.join(job.get('preferred_skills', []))}
        Responsibilities: {', '.join(job.get('responsibilities', []))}
        Company Type: {job.get('company_type')}
        Industry: {job.get('industry')}

        Provide a detailed analysis in JSON format:
        {{
            "overall_score": 0.85,
            "strengths": [
                "Candidate has all required skills",
                "Experience level exceeds requirements",
                "Relevant industry background"
            ],
            "gaps": [
                "Missing experience with specific technology",
                "Limited leadership experience for senior role"
            ],
            "recommendation": "recommend",
            "detailed_reasoning": "Comprehensive explanation of the analysis",
            "key_highlights": [
                "8 years of experience vs 5 required",
                "Python expert matching tech stack",
                "Previous startup experience"
            ],
            "potential_concerns": [
                "No experience with required cloud platform",
                "Career gap of 1 year"
            ]
        }}
        """

        try:
            llm_analysis = extract_json(
                analysis_prompt,
                model="meta-llama/Llama-3.3-70B-Instruct",
                temperature=0.3
            )
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            llm_analysis = {
                "overall_score": 0.5,
                "strengths": ["Unable to analyze with LLM"],
                "gaps": ["Analysis incomplete"],
                "recommendation": "consider",
                "detailed_reasoning": "Analysis unavailable due to error",
                "key_highlights": [],
                "potential_concerns": []
            }

        # Combine quantitative and qualitative analysis
        # Skill score calculation
        skill_score = 0.0
        if required_skills:
            skill_score = len(required_matches) / len(required_skills)
            # Bonus for preferred skills
            if preferred_skills:
                skill_score += (len(preferred_matches) / len(preferred_skills)) * 0.2
            skill_score = min(1.0, skill_score)

        # Experience score already calculated
        exp_score = experience_score

        # Combined quantitative score
        quantitative_score = (skill_score * 0.6) + (exp_score * 0.4)

        # Blend with LLM score
        final_score = (quantitative_score * 0.4) + (llm_analysis.get("overall_score", 0.5) * 0.6)

        return {
            "overall_score": round(final_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(exp_score, 2),
            "skills_match": {
                "required_matches": list(required_matches),
                "preferred_matches": list(preferred_matches),
                "missing_required": list(missing_required),
                "required_match_rate": len(required_matches) / len(required_skills) if required_skills else 0
            },
            "strengths": llm_analysis.get("strengths", []),
            "gaps": llm_analysis.get("gaps", []),
            "recommendation": llm_analysis.get("recommendation", "consider"),
            "detailed_reasoning": llm_analysis.get("detailed_reasoning", ""),
            "key_highlights": llm_analysis.get("key_highlights", []),
            "potential_concerns": llm_analysis.get("potential_concerns", []),
            "quantitative_analysis": {
                "resume_experience": resume_experience,
                "required_experience": required_experience,
                "skill_coverage": f"{len(required_matches)}/{len(required_skills)} required skills"
            }
        }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["match_analysis"] = exec_res
        return "categorize_result"


class ResultCategorizerNode(ConditionalNode):
    """Categorizes results and determines next steps."""

    def __init__(self):
        super().__init__(
            expression="match_analysis['overall_score']",
            outcomes={
                "True": "categorize_by_score",
                "False": "categorize_by_score"
            },
            default_outcome="categorize_by_score",
            node_id="result_categorizer"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "match_analysis": shared.get("match_analysis", {}),
            "params": self.params
        }

    def exec(self, context: Dict[str, Any]) -> str:
        analysis = context["match_analysis"]
        score = analysis.get("overall_score", 0.0)

        # Categorize by score
        if score >= 0.9:
            return "excellent_match"
        elif score >= 0.75:
            return "strong_match"
        elif score >= 0.6:
            return "good_match"
        elif score >= 0.4:
            return "potential_match"
        else:
            return "poor_match"

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["match_category"] = exec_res
        return exec_res


class CategoryProcessorNode(MapperNode):
    """Processes results based on category."""

    def __init__(self):
        config = {
            "sources": ["match_analysis", "match_category", "resume_data", "job_data"],
            "mappings": {
                "category": {"from": "match_category"},
                "score": {"from": "match_analysis", "computed": "match_analysis['overall_score']"},
                "recommendation": {"from": "match_analysis"},
                "priority": {
                    "computed": "'high' if match_category in ['excellent_match', 'strong_match'] else 'medium' if match_category in ['good_match'] else 'low'"
                },
                "next_steps": {
                    "computed": """
                    {
                        'excellent_match': 'Schedule interview immediately - top candidate',
                        'strong_match': 'Schedule interview within 3 days',
                        'good_match': 'Schedule technical screening',
                        'potential_match': 'Keep in talent pool, consider for other roles',
                        'poor_match': 'Reject politely'
                    }.get(match_category, 'Review manually')
                    """
                },
                "interview_format": {
                    "computed": """
                    {
                        'excellent_match': 'On-site with team',
                        'strong_match': 'Video interview with hiring manager',
                        'good_match': 'Phone screen with recruiter',
                        'potential_match': 'Initial call only if needed',
                        'poor_match': 'No interview'
                    }.get(match_category, 'TBD')
                    """
                },
                "candidate_summary": {
                    "computed": "f\"{resume_data.get('name', 'Unknown')} - {job_data.get('title', 'Position')} ({match_analysis['overall_score']:.0%} match)\""
                },
                "key_selling_points": {
                    "from": "match_analysis",
                    "computed": "match_analysis.get('key_highlights', [])[:3]"
                },
                "concerns_to_address": {
                    "from": "match_analysis",
                    "computed": "match_analysis.get('potential_concerns', [])[:2]"
                }
            }
        }
        super().__init__(config, node_id="category_processor")

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        for key, value in exec_res.items():
            shared[key] = value
        return "default"


def create_resume_workflow() -> Graph:
    """Create the complete resume-job matching workflow."""

    # Create nodes
    resume_parser = ResumeParserNode()
    job_parser = JobParserNode()
    match_analyzer = MatchAnalyzerNode()
    result_categorizer = ResultCategorizerNode()
    category_processor = CategoryProcessorNode()

    # Connect nodes
    resume_parser >> job_parser
    job_parser >> match_analyzer
    match_analyzer >> result_categorizer
    result_categorizer >> category_processor

    # Create graph
    return Graph(start=resume_parser)


def format_results(shared: Dict[str, Any]) -> str:
    """Format the final results for display."""

    result = []
    result.append("🎯 RESUME-JOB MATCHING ANALYSIS")
    result.append("=" * 50)

    # Basic info
    resume_data = shared.get("resume_data", {})
    job_data = shared.get("job_data", {})
    match_analysis = shared.get("match_analysis", {})

    result.append(f"👤 Candidate: {resume_data.get('name', 'Unknown')}")
    result.append(f"💼 Position: {job_data.get('title', 'Unknown Position')}")
    result.append(f"📊 Overall Score: {match_analysis.get('overall_score', 0):.1%}")
    result.append(f"🏷️ Category: {shared.get('match_category', 'unknown').replace('_', ' ').title()}")
    result.append("")

    # Recommendation
    result.append("💡 RECOMMENDATION")
    result.append("-" * 20)
    result.append(f"Status: {shared.get('recommendation', 'consider').replace('_', ' ').title()}")
    result.append(f"Next Steps: {shared.get('next_steps', 'Review manually')}")
    result.append(f"Priority: {shared.get('priority', 'medium').title()}")
    result.append("")

    # Skills analysis
    skills_match = match_analysis.get("skills_match", {})
    if skills_match:
        result.append("🛠️ SKILLS ANALYSIS")
        result.append("-" * 20)
        result.append(f"Required Skills Match: {skills_match.get('required_match_rate', 0):.1%}")

        if skills_match.get("required_matches"):
            result.append(f"✅ Matches: {', '.join(skills_match['required_matches'][:3])}")

        if skills_match.get("missing_required"):
            result.append(f"❌ Missing: {', '.join(skills_match['missing_required'][:2])}")

        result.append("")

    # Strengths and gaps
    if match_analysis.get("strengths"):
        result.append("💪 STRENGTHS")
        result.append("-" * 20)
        for strength in match_analysis["strengths"][:3]:
            result.append(f"• {strength}")
        result.append("")

    if match_analysis.get("gaps"):
        result.append("🔍 AREAS FOR CONSIDERATION")
        result.append("-" * 20)
        for gap in match_analysis["gaps"][:3]:
            result.append(f"• {gap}")
        result.append("")

    # Key highlights
    if shared.get("key_selling_points"):
        result.append("⭐ KEY SELLING POINTS")
        result.append("-" * 20)
        for point in shared["key_selling_points"]:
            result.append(f"• {point}")
        result.append("")

    # Concerns
    if shared.get("concerns_to_address"):
        result.append("⚠️ CONCERNS TO ADDRESS")
        result.append("-" * 20)
        for concern in shared["concerns_to_address"]:
            result.append(f"• {concern}")
        result.append("")

    # Interview details
    result.append("📅 INTERVIEW DETAILS")
    result.append("-" * 20)
    result.append(f"Format: {shared.get('interview_format', 'TBD')}")
    result.append("")

    return "\n".join(result)


def run_demo_scenarios():
    """Run demonstration scenarios."""

    # Test scenarios
    scenarios = [
        {
            "name": "Excellent Match - Senior Developer",
            "resume": """
            Name: Sarah Chen
            Experience: Senior Software Engineer with 8 years of experience
            Skills: Python, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS
            Education: MS Computer Science from MIT
            Previous Companies: Google, Amazon, Stripe
            Achievements: Led team of 6 engineers, improved system performance by 40%
            """,
            "job": """
            Position: Senior Python Developer
            Required Experience: 5+ years
            Required Skills: Python, Django, PostgreSQL
            Preferred Skills: Redis, Docker, AWS
            Responsibilities: Lead development of cloud applications, mentor junior developers
            Company Type: Enterprise
            Industry: Technology
            Remote Work: Yes
            """
        },
        {
            "name": "Partial Match - Career Changer",
            "resume": """
            Name: Michael Rodriguez
            Experience: 3 years as Data Analyst transitioning to software development
            Skills: Python (basic), SQL, Excel, Tableau, Statistics
            Education: BA Economics from State University
            Previous Companies: Acme Corp, Data Insights Inc
            Achievements: Improved reporting efficiency by 25%
            """,
            "job": """
            Position: Senior Python Developer
            Required Experience: 5+ years
            Required Skills: Python, Django, PostgreSQL
            Preferred Skills: Redis, Docker, AWS
            Responsibilities: Lead development of cloud applications, mentor junior developers
            Company Type: Enterprise
            Industry: Technology
            Remote Work: Yes
            """
        },
        {
            "name": "Poor Match - Wrong Background",
            "resume": """
            Name: Jennifer Kim
            Experience: Marketing Manager with 6 years of experience
            Skills: Marketing, SEO, Social Media, Content Writing, Analytics
            Education: BA Marketing from Business School
            Previous Companies: Marketing Agency, Retail Corp
            Achievements: Increased brand awareness by 60%
            """,
            "job": """
            Position: Senior Python Developer
            Required Experience: 5+ years
            Required Skills: Python, Django, PostgreSQL
            Preferred Skills: Redis, Docker, AWS
            Responsibilities: Lead development of cloud applications, mentor junior developers
            Company Type: Enterprise
            Industry: Technology
            Remote Work: Yes
            """
        }
    ]

    workflow = create_resume_workflow()

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"📋 SCENARIO {i}: {scenario['name']}")
        print(f"{'='*60}")

        # Initialize shared state
        shared = {
            "resume_text": scenario["resume"],
            "job_text": scenario["job"],
            "scenario_name": scenario["name"]
        }

        try:
            # Run workflow
            workflow.run(shared)

            # Format and display results
            results = format_results(shared)
            print(results)

        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            logger.error(f"Workflow error: {e}")


def main():
    """Main demonstration function."""
    print("🎯 Resume-Job Matching Workflow")
    print("=" * 60)
    print("A production-ready workflow that analyzes resumes against")
    print("job descriptions and provides detailed matching analysis.")
    print()

    try:
        # Test API connection
        from utils.call_llm import test_connection
        if not test_connection():
            print("⚠️ Warning: LLM API connection test failed.")
            print("   The workflow will run but may have limited functionality.")
            print()

        # Run demonstration scenarios
        run_demo_scenarios()

        print(f"\n{'='*60}")
        print("🎉 Resume matching workflow demonstration completed!")
        print(f"{'='*60}")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nCheck that:")
        print("1. All required packages are installed")
        print("2. LLM API configuration is correct")
        print("3. Configuration files are present")


if __name__ == "__main__":
    main()