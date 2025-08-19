from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start
from purchase_copilot.crews.cleaning_crew.cleaning_crew import CleaningCrew
from purchase_copilot.crews.score_crew.score_crew import ScoreCrew
from purchase_copilot.utils import *
import json
import requests
import os
import pandas as pd
from typing import List, Optional
import pandas as pd
from pydantic import BaseModel, Field


class GlobalState(BaseModel):
    input_link: str = ""
    input_seitnummer: int = -1
    input_interest: str = ""

    pages : List[str] = Field(default_factory=list)
    # links to houses 
    links: List[List[str]] = Field(default_factory=list)
    links_content: List[List[str]] = Field(default_factory=list)
    links_cleaned_content: List[List[str]] = Field(default_factory=list)
    links_scored_content: List[List[str]] = Field(default_factory=list)


class RetrieveFlow(Flow[GlobalState]):

    @start()
    def get_links_from_page(self) -> None:
        try:
            print("Getting links...")
            self.state.input_link = os.environ.get("INPUT_LINK", "")
            print("hellooo",self.state.input_link)
            self.state.input_seitnummer = int(os.environ.get("INPUT_SEITNUMMER", ""))
            self.state.input_interest = os.environ.get("INPUT_INTEREST", "")
            all_pages = generate_page_list(self.state.input_seitnummer, self.state.input_link)
            self.state.pages = all_pages
            for page in all_pages:
                response = requests.get(page, timeout=10)
                response.raise_for_status()
                page_text = response.text
                links = extract_item_list(page_text)[1:3]
                self.state.links.append(links)
            print("links",self.state.links)
        except Exception as e:
            print(f"Unexpected error in get_links: {e}")

    @listen(get_links_from_page)
    async def extract_text_from_links(self) -> None:
        contents: List[List[str]] = []
        for i, link_group in enumerate(self.state.links):
            page_texts: List[str] = []
            for link in link_group:
                await take_screenshot(link)
                raw_text = extract_text_from_image("./screenshot.png")
                screenshot_text = trim(raw_text) if raw_text else ""
                page_texts.append(screenshot_text)
            contents.append(page_texts)
        self.state.links_content = contents
        print("links_content",self.state.links_content)

    @listen(extract_text_from_links)
    def organize_and_retrieve(self) -> None:
        """Clean extracted content using CleaningCrew."""
        print("Cleaning extracted content...")
        cleaned_contents: List[List[dict]] = []   # store only JSON dicts
        for group_content in self.state.links_content:
            result = []
            for content in group_content:
                cleaned_result = CleaningCrew().crew().kickoff(inputs={"content": content})
                raw_output = cleaned_result.raw
                # 1. remove <think>...</think> reasoning if present
                if "<think>" in raw_output:
                    raw_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL)
                # 2. try to parse JSON
                try:
                    parsed = json.loads(raw_output.strip())
                except Exception as e:
                    print(f"Could not parse cleaned content: {e}")
                    parsed = raw_output.strip()
                result.append(parsed)
            cleaned_contents.append(result)
        self.state.links_cleaned_content = cleaned_contents
        print("links_cleaned_content", self.state.links_cleaned_content)

    @listen(organize_and_retrieve)
    def score(self) -> None:
        """Score cleaned content according to interest using ScoreCrew."""
        print("Scoring cleaned content...")
        scored_contents: List[List[int]] = []   # store only numbers
        for content_group in self.state.links_cleaned_content:
            result = []
            for content in content_group:
                scored_result = ScoreCrew().crew().kickoff(
                    inputs={"content": content, "interest": self.state.input_interest}
                )
                score_value = None
                if isinstance(scored_result.raw, int):
                    score_value = scored_result.raw
                else:
                    try:
                        parsed = json.loads(scored_result.raw)
                        score_value = parsed.get("score", None)
                    except Exception as e:
                        score_value = scored_result.raw
                result.append(score_value)
            scored_contents.append(result)
        self.state.links_scored_content = scored_contents
        print("links_scored_content", self.state.links_scored_content)

        # --- Create DataFrame in expanded form ---
        df = pd.DataFrame({
            "page": self.state.pages,
            "links": self.state.links,
            "raw_content": self.state.links_content,
            "cleaned_content": self.state.links_cleaned_content,
            "score": self.state.links_scored_content,   # store only score
        })
        # expand rows
        df = df.set_index("page").apply(pd.Series.explode).reset_index()

        df.to_csv("retrieved_data.csv", index=False)
        print("Data saved to retrieved_data.csv")

def kickoff() -> None:
    flow = RetrieveFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()
