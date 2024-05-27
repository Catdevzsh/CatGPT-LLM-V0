import os
from openai import OpenAI
from crewai import Agent, Task, Crew, Process
from langchain.tools import DuckDuckGoSearchRun
import tkinter as tk
from tkinter import ttk

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1")

# Initialize search tool
search_tool = DuckDuckGoSearchRun()

# Define a custom LLM class to wrap the OpenAI completions API
class CustomLLM:
    def __init__(self, client):
        self.client = client

    def bind(self, **kwargs):
        def generate(prompt):
            completion = self.client.completions.create(
                model="LM Studio Community/Meta-Llama-3-8B-Instruct-GGUF",
                prompt=prompt,
                **kwargs
            )
            return completion.choices[0].text
        return generate

# Create AI agent with the custom LLM
ai_agent = Agent(
    role='AI Assistant',
    goal='Assist the user by generating output based on their prompt',
    backstory="""You are an AI assistant created to help users by taking their prompt as input and generating relevant output.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=CustomLLM(client),
)

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Assistant 1.0 [Beta] - Local Server 1.0 [C] Flames Labs 20XX")
        self.geometry("600x400")
        self.resizable(False, False)

        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background="#343541", foreground="white")
        style.configure("TEntry", fieldbackground="#808080")
        style.configure("TButton", background="#444654", foreground="white")
        style.map("TButton", background=[("active", "#565869")])

    def create_widgets(self):
        self.chat_history = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED, bg="#D2B48C", fg="#008000")
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.user_input = ttk.Entry(input_frame, style="TEntry")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=(10, 0))

        self.bind("<Return>", lambda event: self.send_message())

        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "AI Assistant: Hello! I'm an AI assistant. Please provide a prompt and I will generate relevant output.\n\n")
        self.chat_history.configure(state=tk.DISABLED)

    def send_message(self):
        user_prompt = self.user_input.get()
        self.user_input.delete(0, tk.END)

        self.update_chat_history(f"User Prompt: {user_prompt}\n\n")

        task = Task(
            description=f"""Generate relevant output based on the following user prompt: {user_prompt}""",
            agent=ai_agent
        )

        crew = Crew(agents=[ai_agent], tasks=[task], verbose=2, process=Process.sequential)
        result = crew.kickoff()

        self.update_chat_history(f"AI Assistant Output: {result}\n\n")

    def update_chat_history(self, message):
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message)
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)

# Run the application
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
