from openai import OpenAI

class Messager:
    def __init__(self, api_key, url):
        self.SystemPrompt = "You are a translation engine that strictly translates English sentences into Turkish. You do not offer explanations, alternatives, or commentary. You only output the full and final translation in Turkish, nothing else."
        self.client = OpenAI(
            api_key=api_key,
            base_url=url
        )
        self.history = []
        self.model = ""

    def SelectModel(self, model):
        self.model = model

    def AddToHistory(self, role, content):
        self.history.append({
            "role" : role,
            "content" : content
        })

    def Clear(self):
        self.history.clear()
    
    def Message(self, content, doNotAddHistory = False):
        if len(self.history) < 1:
            self.AddToHistory("system", self.SystemPrompt)
        
        self.AddToHistory("user", content)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0.7,
        )
        if doNotAddHistory == False:
            self.AddToHistory(response.choices[0].message.role, response.choices[0].message.content)
        return (response.choices[0].message.role, response.choices[0].message.content)

    def his(self):
        return self.history