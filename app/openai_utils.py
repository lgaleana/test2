import openai

def generate_headline(text: str, image_url: str) -> str:
    prompt = f"Generate an ad headline for the following image URL based on the website text:\n\nWebsite Text:\n{text}\n\nImage URL: {image_url}\n\nAd Headline:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    return response.choices[0].message['content'].strip()

