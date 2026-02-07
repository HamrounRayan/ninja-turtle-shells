import requests
import re

class AiAgent:
    def __init__(self):
        self.API_KEY = "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"
        self.MODEL = "z-ai/glm-4.5-air:free"
        
    def ask(self, prompt):
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()
    
    def __call__(self, projects):
        """Make the agent callable - just pass in the projects and get them back ranked!"""
        if not projects:
            return projects
            
        projects_info = "\n".join([
            f"Project {i+1}: Name: {p['name']}, Address: {p['address']}"
            for i, p in enumerate(projects)
        ])
        
        prompt = f"""Rank these projects by educational value, innovation, and real-world impact:

{projects_info}

Return ONLY comma-separated numbers (e.g., "3,1,2"). Nothing else."""
        
        try:
            ranking_str = self.ask(prompt)
            print(f"AI Response: {ranking_str}")  # Debug print
            
            # Extract just the numbers using regex
            numbers = re.findall(r'\d+', ranking_str)
            
            if not numbers:
                print("AI didn't return valid numbers, returning original order")
                return projects
            
            ranked_indices = [int(x) - 1 for x in numbers]
            
            # Return the same JSONs, just reordered!
            return [projects[i] for i in ranked_indices if 0 <= i < len(projects)]
        except Exception as e:
            print(f"Error ranking projects: {e}")
            return projects  # Return original order if something breaks