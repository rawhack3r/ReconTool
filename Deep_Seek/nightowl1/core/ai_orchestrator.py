import openai
import yaml

class AIOrchestrator:
    def __init__(self):
        with open('config/tool_config.yaml') as f:
            self.tools = yaml.safe_load(f)['tools']
        
    def recommend_tools(self, target, history):
        prompt = f"""
        Target: {target}
        Previous findings: {str(history)[:1000]}
        Available tools: {list(self.tools.keys())}
        
        Recommend 3-5 tools in order of priority with justification.
        Output format: 
        - tool_name: reason
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return self.parse_recommendations(response.choices[0].message['content'])
    
    def parse_recommendations(self, text):
        recommendations = {}
        for line in text.split('\n'):
            if ':' in line:
                tool, reason = line.split(':', 1)
                recommendations[tool.strip()] = reason.strip()
        return recommendations