import yaml

def load_agents(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_tasks(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)
# /Users/bhupatiraju/Downloads/financial-document-analyzer-debug/financial_document_analyzer/src/financial_document_analyzer/config/agents.yaml
