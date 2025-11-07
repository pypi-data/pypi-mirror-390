from multi_ai_handler import request_ai

def main():
    print(request_ai(system_prompt="You're a helpful assistant", user_text="Hello", file="test/2024-10-31_aliexpress_02.pdf", provider="ollama"))

if __name__ == "__main__":
    main()
