import asyncio
from src.agent import AutomationAgent

async def main():
    agent = await AutomationAgent().initialize()
    
    while True:
        task = input("Enter your task (or 'quit' to exit): ")
        if task.lower() == 'quit':
            break
            
        await agent.run(task)
        print("\n--- Task completed! Ready for next task ---\n")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
