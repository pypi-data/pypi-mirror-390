"""
Example demonstrating how to send a GIF using the send_gif method.
"""

from interpal import InterpalClient

# Initialize client with credentials
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True
)

# Thread ID to send the GIF to
thread_id = '1833435079742223361'

# GIF URL (e.g., from Giphy)
gif_url = 'https://media3.giphy.com/media/v1.Y2lkPTU4YWY4YzA5a2Rldmp6NTZ2c2RhN21seGp1NjVyZGQ1czJna21qZmxqcWI4eG0zaCZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/YOuRCwUvMTQRX3TA7s/giphy-preview.gif'

# Send the GIF
response = client.send_gif(
    thread_id=thread_id,
    gif_url=gif_url,
    tmp_id='34bc'  # Optional
)

print(f"GIF sent successfully!")
print(f"Message ID: {response.id if hasattr(response, 'id') else 'N/A'}")
print(f"Response: {response}")

# You can also use the messages API directly
response2 = client.messages.send_gif(
    thread_id=thread_id,
    gif_url='https://media.giphy.com/media/some_other_gif_id/giphy.gif'
)

print(f"\nSecond GIF sent!")

