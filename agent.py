from langgraph.graph import StateGraph
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tools import TOOLS
import traceback
from typing import TypedDict, Any

# Data flow 
class AgentState(TypedDict):
    df: Any
    question: str
    tool: str
    answer: Any

# Model used 
llm = ChatOpenAI(temperature=0, model="azure.gpt-4o")

# Format available tools into a string to help the LLM decide
tool_list_str = "\n".join([f"- {name}: {func.__doc__}" for name, func in TOOLS.items()])

# Prompt
planner_prompt = PromptTemplate.from_template(f"""
You are an intelligent agent helping a user analyze a pandas DataFrame.

Available tools:
{tool_list_str}

Only return the tool name that best fits this question:
"{{question}}"

If the user wants averages grouped by column, return average_by_column.
""")

# Node 1: Planner node ----- (decides LLM action)
def planner_node(state: AgentState) -> AgentState:
    question = state["question"]
    tool_choice = llm.predict(planner_prompt.format(question=question)).strip()
    return {"tool": tool_choice, "question": question, "df": state["df"], "answer": None}

# Node 2: Executor node ------  (calls tool and does the work on dataframe)
def executor_node(state: AgentState) -> AgentState:
    tool_name = state["tool"]
    df = state["df"]
    question = state["question"]
    
 #if avg by col, parse the col from question & 
 #call tool with df, col; else run with df 
    try:
        if tool_name == "average_by_column":
            for col in df.columns:
                if col.lower() in question.lower():
                    result = TOOLS[tool_name](df, col)
                    return {**state, "answer": result}
            return {**state, "answer": " Couldn't determine the column to group by."}
        else:
            result = TOOLS[tool_name](df)
            return {**state, "answer": result}

    except Exception as e:
        return {
            **state,
            "answer": f"Tool `{tool_name}` failed:\n{e}\n\n{traceback.format_exc()}"
        }

#Route , conditional edge 
def run_agent(df, question):
    graph = StateGraph(AgentState)
    graph.add_node("plan", planner_node)
    graph.add_node("execute", executor_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.set_finish_point("execute")

    result = graph.compile().invoke({
        "df": df,
        "question": question,
        "tool": "",
        "answer": None
    })

    return result["answer"]

#add more agents, langchain for orchatsor