import requests
class AiAgent:
    def __init__(self):
        self.API_KEY = "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"
        self.MODEL = "x-ai/grok-4.1-fast"

    def ask(self, prompt):
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        if response.status_code != 200:
            print("❌ Error:", response.text)
            return

        content = response.json()["choices"][0]["message"]["content"]
        print(f"\n🐉: {content.strip()}\n")

    # def main():
    #     while True:
    #         try:
    #             prompt = input("> ").strip()
    #             if not prompt:
    #                 continue
    #             if prompt.lower() in ['exit', 'quit']:
    #                 break
    #             ask(prompt)
    #         except KeyboardInterrupt:
    #             print("\n Bye.")
    #             break

    # if __name__ == "__main__":
    #     main()

