from src.playwright_actions import PlaywrightActions
from src.ai_actions import Anthropic
from src.sound_player import SoundPlayer
import json
import re
from src.prompts import execution_prompt

class AutomationAgent:
    def __init__(self):
        self.anthropic = Anthropic()
        self.previous_actions = []
        self.playwright = None
        self.sound_player = SoundPlayer()
        
    async def initialize(self):
        self.playwright = await PlaywrightActions().initialize()
        return self
        
    async def execute_action(self, action_data):
        action_type = action_data["action"]
        
        if action_type == "navigation":
            return await self.playwright.navigate(action_data["url"])
            
        elif action_type == "click":
            selector = action_data["selector"]
            nth = 0
            if ", nth=" in selector:
                selector, nth_part = selector.rsplit(", nth=", 1)
                nth = int(nth_part)
            
            selector_type, selector_name = selector.split("=", 1)
            return await self.playwright.click_element(selector_type, selector_name, nth)
            
        elif action_type == "fill":
            selector = action_data["selector"]
            nth = 0
            if ", nth=" in selector:
                selector, nth_part = selector.rsplit(", nth=", 1)
                nth = int(nth_part)
            
            selector_type, selector_name = selector.split("=", 1)
            message = await self.playwright.fill_input(
                selector_type, 
                selector_name, 
                action_data["value"],
                nth
            )
            await self.playwright.press_key("Enter")
            return message

        elif action_type == 'finished':
            self.sound_player.play("Glass")
            return True 
        
        elif action_type == "ask_human":
            self.sound_player.play("Ping") 
            print(f"Please provide the following information: {action_data['question_to_human']}")
            user_input = input("> ")
        
        return f"Unknown action type: {action_type}"

    async def cleanup(self):
        if self.playwright:
            await self.playwright.close()

    async def run(self, task: str):
        try:
            self.previous_actions = []
            
            while True:
                success, accessibility_tree = await self.playwright.get_parsed_accessibility_tree()
                if not success:
                    print(f"Error getting accessibility tree: {accessibility_tree}")
                    break
                
                screenshot_path = "screenshot.png"
                success, screenshot_msg = await self.playwright.take_screenshot(screenshot_path)
                if not success:
                    print(f"Error taking screenshot: {screenshot_msg}")
                    break

                system_message = execution_prompt
                user_message = (f"Task: {task}\n"
                              f"Previous actions: {self.previous_actions}\n"
                              f"Current accessibility tree: {accessibility_tree}")
                
                response = await self.anthropic.get_response(
                    system_message=system_message,
                    user_message=user_message,
                    image_path=screenshot_path
                )

                response = json.loads(response)

                print(f'Agent Reasoning: {response["reasoning"]}')
                print(f'Agent Action: {response["action"]}')

                if response["action"] == "finished":
                    self.sound_player.play("Glass")
                    break
                
                result = await self.execute_action(response)
                print(f'Action Result: {result}')
                print('--------------------------------')

                self.previous_actions.append({
                    "action": response,
                    "result": result
                })
                await self.playwright.wait_for_load_state('load')
                
        finally:
            pass
