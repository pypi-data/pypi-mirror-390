"""
Example demonstrating how to send a GIF using the async send_gif method.
"""

import asyncio
from interpal import AsyncInterpalClient

async def main():
    # Initialize async client with credentials
    client = AsyncInterpalClient(
        username="your_username",
        password="your_password"
    )
    
    # Login
    client.login()
    
    # Thread ID to send the GIF to
    thread_id = '1833435079742223361'
    
    # GIF URL (e.g., from Giphy)
    gif_url = 'https://media3.giphy.com/media/v1.Y2lkPTU4YWY4YzA5a2Rldmp6NTZ2c2RhN21seGp1NjVyZGQ1czJna21qZmxqcWI4eG0zaCZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/YOuRCwUvMTQRX3TA7s/giphy-preview.gif'
    
    # Send the GIF
    response = await client.send_gif(
        thread_id=thread_id,
        gif_url=gif_url,
        tmp_id='34bc'  # Optional
    )
    
    print(f"GIF sent successfully!")
    print(f"Message ID: {response.id if hasattr(response, 'id') else 'N/A'}")
    print(f"Response: {response}")
    
    # You can also use the messages API directly
    response2 = await client.messages.send_gif(
        thread_id=thread_id,
        gif_url='https://media.giphy.com/media/some_other_gif_id/giphy.gif'
    )
    
    print(f"\nSecond GIF sent!")
    
    # Clean up
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

