from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

load_dotenv()
API_KEY = os.environ["GEMINI_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", 
                             google_api_key=API_KEY,
                             temperature=0)

class CleaningState(BaseModel):

    input_text: str
    structured_response: str = ""

class Ai_agent:
    def __init__(self):
        self.graph = self.create_graph()

    @staticmethod
    def _response_to_text(response):
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
                else:
                    parts.append(str(item))

            return "\n".join(parts)

        return str(content)

    def create_graph(self):
        graph = StateGraph(CleaningState)

        def agent_logic(state: CleaningState) -> CleaningState:

            response = llm.invoke(state.input_text)
            structured_response = self._response_to_text(response)
            return CleaningState(input_text=state.input_text, structured_response=structured_response)
    
        graph.add_node("cleaning_agent", agent_logic)
        graph.add_edge("cleaning_agent", END)
        graph.set_entry_point("cleaning_agent")
        
        return graph.compile()
    
    def process_data(self, df, batch_size=20):
        if df.empty:
            return "Dataset is empty."

        cleaned_response = []

        for i in range(0, len(df), batch_size):
            df_batch = df.iloc[i:i + batch_size]

            prompt = f"""
                You are an AI Data Cleaner Agent. Analyze the dataset:
                {df_batch.to_string()}
                Identify missing values, choose the best imputation strategy(mean, median, mode, drop),
                remove duplicates, deal with outliers and format text correctly.

                Return cleaned data. """
            
            state = CleaningState(input_text=prompt, structured_response="")
            response = self.graph.invoke(state)

            if isinstance(response, dict):
                response = CleaningState(**response)

            cleaned_response.append(response.structured_response)

        return "\n".join(cleaned_response)