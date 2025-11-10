import os
from pathlib import Path
from crewai import Crew, Agent, Task, Process
from crewai_tools import FileReadTool
from tools.pdf_ingestion_tool import PDFIngestionTool
from tools.investment_tool import InvestmentTool
from tools.risk_assessment_tool import RiskAssessmentTool, StatsTool, CalculatorTool
from utils.yaml_loader import load_agents, load_tasks

from crewai import LLM
import os

llm = LLM(
    provider="groq",
    model="llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------------------------------------------------
# BASE PATH CONFIGURATION
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

AGENTS_PATH = BASE_DIR / "config" / "agents.yaml"
TASKS_PATH = BASE_DIR / "config" / "tasks.yaml"
DOCUMENT_PATH = BASE_DIR / "knowledge" / "TSLA-Q2-2025-Update.pdf"

# ---------------------------------------------------------------------------
# LOAD YAML CONFIGURATIONS
# ---------------------------------------------------------------------------
agents_config = load_agents(AGENTS_PATH)
tasks_config = load_tasks(TASKS_PATH)

# ---------------------------------------------------------------------------
# INITIALIZE TOOLS
# ---------------------------------------------------------------------------
pdf_ingestion_tool = PDFIngestionTool(document_path=str(DOCUMENT_PATH))
investment_tool = InvestmentTool()
risk_assessment_tool = RiskAssessmentTool()
file_reader = FileReadTool(file_path=str(DOCUMENT_PATH))

# ---------------------------------------------------------------------------
# BUILD AGENTS
# ---------------------------------------------------------------------------
agents = {}
for name, data in agents_config.items():
    tool_instances = []
    for tool_name in data.get("tools", []):
        if tool_name == "pdf_ingestion_tool":
            tool_instances.append(pdf_ingestion_tool)
        elif tool_name == "investment_tool":
            tool_instances.append(investment_tool)
        elif tool_name == "risk_assessment_tool":
            tool_instances.append(risk_assessment_tool)

    agents[name] = Agent(
        role=data["role"],
        goal=data["goal"],
        backstory=data["backstory"],
        config=data["config"],
        tools=tool_instances,
        llm=llm,
    )

# ---------------------------------------------------------------------------
# BUILD TASKS
# ---------------------------------------------------------------------------
tasks = {}
for name, data in tasks_config.items():
    task_tools = []
    for tool_name in data.get("tools", []):
        if tool_name == "pdf_ingestion_tool":
            task_tools.append(pdf_ingestion_tool)
        elif tool_name == "investment_tool":
            task_tools.append(investment_tool)
        elif tool_name == "risk_assessment_tool":
            task_tools.append(risk_assessment_tool)

    context_list = [
        tasks_config[c]["description"]
        for c in data.get("context", [])
        if c in tasks_config
    ]

    tasks[name] = Task(
        description=data["description"],
        expected_output=data["expected_output"],
        agent=agents[data["agent"]],
        tools=task_tools,
        context=context_list,
        async_execution=data.get("async_execution", False),
    )

# ---------------------------------------------------------------------------
# BUILD THE CREW (exported for use in main.py)
# ---------------------------------------------------------------------------
crew = Crew(
    agents=list(agents.values()),
    tasks=list(tasks.values()),
    process=Process.sequential,
    verbose=True,
)

