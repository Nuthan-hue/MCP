import requests

def main():
    # Step 1: Decide the task based on user input
    user_input = "Summarize my latest email"

    if "summarize" in user_input.lower() and "email" in user_input.lower():
        print("🧠 Task identified: summarize email")

        # Step 2: Call the email MCP server to get the latest email
        email_response = requests.post(
            "http://localhost:8001/read_emails",
            json={"filter": "unread", "count": 1}
        )
        email_response.raise_for_status()
        email_data = email_response.json()[0]  # Assuming one email

        print(f"\n📨 Email Fetched:\nSubject: {email_data['subject']}\nBody: {email_data['body']}\n")

        # Step 3: Call the LLM MCP server to summarize the email body
        llm_response = requests.post(
            "http://localhost:8002/summarize",
            json={"input": email_data["body"]}
        )
        llm_response.raise_for_status()
        summary = llm_response.json()["summary"]

        # Step 4: Display result
        print(f"📋 Summary:\n{summary}")

    else:
        print("⚠️ Unknown task.")

if __name__ == "__main__":
    main()
