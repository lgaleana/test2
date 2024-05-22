from openai import OpenAI

def generate_headline(client, text: str, image_url: str) -> str:
    prompt = (
        f"Generate an ad headline for the following image URL based on the website text. "
        f"The headline should be no more than 5 words long:\n\n"
        f"Website Text:\n{text}\n\n"
        f"Image URL: {image_url}\n\n"
        f"Ad Headline:"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()
