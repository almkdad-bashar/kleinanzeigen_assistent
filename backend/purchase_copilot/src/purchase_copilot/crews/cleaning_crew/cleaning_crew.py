from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from purchase_copilot.llm_config import *

@CrewBase
class CleaningCrew():
    """CleaningCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def cleaner(self) -> Agent:
        return Agent(
            config=self.agents_config['cleaner'], # type: ignore[index]
            verbose=True,
            llm=llm
        )

    @task
    def organize_task(self) -> Task:
        return Task(
            config=self.tasks_config['organize_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CleaningCrew crew"""

        return Crew(
            agents=[self.cleaner()],
            tasks=[
                self.organize_task()
                   ],
            process=Process.sequential,
            verbose=True,
        )
