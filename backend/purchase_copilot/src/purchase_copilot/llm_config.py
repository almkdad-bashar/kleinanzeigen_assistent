from crewai import LLM

# llm = LLM(
#     model="ollama/llama3",
#     base_url="http://172.17.0.3:11434"
# )

llm = LLM(
    model="ollama/qwen3:1.7b",
    base_url="http://172.17.0.2:11434"
)

