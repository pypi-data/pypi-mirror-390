from multi_ai_handler import request_ai

def main():
    print(request_ai(system_prompt="You're a helpful assistant", user_text="Hello", provider="google"))

if __name__ == "__main__":
    main()
