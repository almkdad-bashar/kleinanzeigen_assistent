from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from purchase_copilot.llm_config import *

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ScoreCrew():
    """ScoreCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def scorer(self) -> Agent:
        return Agent(
            config=self.agents_config['scorer'],
            verbose=True,
            llm=llm
        )

    @task
    def score_task(self) -> Task:
        return Task(
            config=self.tasks_config['score_task'], 
        )


    @crew
    def crew(self) -> Crew:
        """Creates the ScoreCrew crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
