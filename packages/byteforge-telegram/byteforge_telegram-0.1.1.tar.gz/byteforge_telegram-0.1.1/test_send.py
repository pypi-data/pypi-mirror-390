#!/usr/bin/env python3
"""
Throwaway script to test the send_message_sync fix.
This tests that the sync method properly blocks and returns actual results.
"""
import os
import asyncio
from byteforge_telegram.notifier import TelegramBotController

# Get credentials from environment
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
    exit(1)

print("Testing send_message_sync()...")
print(f"Bot token: {BOT_TOKEN[:10]}...")
print(f"Chat ID: {CHAT_ID}")

# Initialize controller
controller = TelegramBotController(BOT_TOKEN)

# Test 1: Basic sync call (no event loop)
print("\n=== Test 1: Sync context (no event loop) ===")
result = controller.send_message_sync(
    text="🧪 Test 1: Basic sync call - if you see this, send_message_sync() works in sync context!",
    chat_ids=[CHAT_ID]
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

# Test 2: Sync call from inside async context (the bug scenario)
print("\n=== Test 2: Async context (the bug fix scenario) ===")

async def test_from_async_context():
    """Call send_message_sync from inside an async function."""
    print("Inside async function, calling send_message_sync()...")
    result = controller.send_message_sync(
        text="🧪 Test 2: Sync call from async context - if you see this, the bug fix works!",
        chat_ids=[CHAT_ID]
    )
    print(f"Result: {result}")
    print(f"Success: {result.get(CHAT_ID, False)}")
    return result

# Run the async test
result = asyncio.run(test_from_async_context())

# Test 3: Formatted message
print("\n=== Test 3: Formatted message sync ===")
result = controller.send_formatted_sync(
    title="Bug Fix Test",
    fields={
        "Status": "✅ Fixed",
        "Issue": "send_message_sync() blocking",
        "Method": "ThreadPoolExecutor approach"
    },
    chat_ids=[CHAT_ID],
    emoji="🔧",
    footer="If you see this message formatted correctly, the fix works!"
)
print(f"Result: {result}")
print(f"Success: {result.get(CHAT_ID, False)}")

print("\n✅ All tests completed! Check your Telegram for 3 messages.")
