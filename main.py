import os
import datetime
import smtplib
from email.message import EmailMessage
from google import genai
from google.genai.types import GenerateContentConfig, Tool, GoogleSearch

def main():
    # 1. Pull secure credentials from environment variables
    # We switch the secret name to GEMINI_API_KEY
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # 16-character App Password

    if not all([GEMINI_API_KEY, EMAIL_ADDRESS, EMAIL_PASSWORD]):
        raise ValueError("Missing required environment variables.")

    # Initialize the official Google GenAI client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""
    Today's date is {today}.
    Act as an expert quantitative and technical stock market analyst for the Indian Stock Market (NSE/BSE). 

    First, execute a web search to retrieve the most recent closing data of the US stock markets (S&P 500, Nasdaq, Dow Jones) from last night, and the current live morning trading level/movement of the Gift Nifty 50. 

    Based on this global sentiment and current pre-market indicators, provide a highly structured intraday trading briefing for today. 

    Please format your response exactly as follows:

    1. Global Market Context: A brief summary of US market performance and the live Gift Nifty status. State clearly what this indicates for the Indian market opening (Gap up / Gap down / Flat).
    2. Sector Watch: Identify 2 specific Indian sectors likely to show high momentum today based on current fundamental news or global cues.
    3. Intraday Watchlist: Provide exactly 3 Large-Cap, 3 Mid-Cap, and 3 Small-Cap Indian stocks to watch today. For every stock, provide:
       * Company Name (Ticker)
       * The Catalyst: A 1-sentence rationale (mentioning technical breakout levels, volume spikes, or overnight fundamental news).
       * Levels: Key Support and Resistance levels to watch for entry/exit.

    Keep the output highly scannable using bolding and bullet points. Do not include generalized financial disclaimers; focus purely on the data and analysis.
    """

    print("Executing live web search and generating watchlist with Gemini...")
    
    response = client.models.generate_content(
        model='gemini-2.5-pro', 
        contents=prompt,
        config=GenerateContentConfig(
            tools=[Tool(google_search=GoogleSearch())],
            thinking_config={
                "thinking_budget": 2048 # Upped the reasoning budget to let 3.1 Pro deep-dive into the technical levels
            }
        )
    )
    
    analysis_text = response.text

    # 2. Construct and dispatch the report via SMTP
    print("Drafting email notification...")
    msg = EmailMessage()
    msg.set_content(analysis_text)
    msg['Subject'] = f'Pre-Market Intraday Watchlist - {today}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    print("Connecting to secure SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("🚀 Success! Grounded Gemini Watchlist delivered to your inbox.")

if __name__ == "__main__":
    main()
