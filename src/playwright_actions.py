from playwright.async_api import async_playwright

class PlaywrightActions():
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self):
        playwright_instance = await async_playwright().start()
        self.browser = await playwright_instance.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            viewport={'width': 896, 'height': 1024}
        )
        self.page = await self.context.new_page()
        return self
    

    async def get_accessibility_snapshot(self):
        try:
            snapshot = await self.page.accessibility.snapshot()
            return True, snapshot
        except Exception as e:
            return False, f"Failed to get accessibility snapshot: {str(e)}"

    def parse_accessibility_tree(self, node, indent=0):
        res = ""
        
        def _parse_node(node, indent, res):
            if not node or 'role' not in node:
                return res

            if not hasattr(_parse_node, 'element_counts'):
                _parse_node.element_counts = {}

            indented_space = " " * indent
            element_key = f"{node['role']}_{node.get('name', 'No name')}"
            
            if element_key not in _parse_node.element_counts:
                _parse_node.element_counts[element_key] = 0
            else:
                _parse_node.element_counts[element_key] += 1
            
            nth_index = _parse_node.element_counts[element_key]
            nth_suffix = f", nth={nth_index}"
            
            if 'value' in node:
                res = res + f"{indented_space}Role: {node['role']} - Name: {node.get('name', 'No name')} - Value: {node['value']}{nth_suffix}\n"
            else:
                res = res + f"{indented_space}Role: {node['role']} - Name: {node.get('name', 'No name')}{nth_suffix}\n"
            
            if 'children' in node:
                for child in node['children']:
                    res = _parse_node(child, indent + 2, res)
                    
            return res

        return _parse_node(node, indent, res)

    async def get_parsed_accessibility_tree(self, indent=0):
        try:
            success, snapshot = await self.get_accessibility_snapshot()
            if not success:
                return False, snapshot
            
            parsed_tree = self.parse_accessibility_tree(snapshot, indent)
            return True, parsed_tree
            
        except Exception as e:
            return False, f"Failed to get and parse accessibility tree: {str(e)}"

    async def navigate(self, url):
        try:
            await self.page.goto(url)
            return f"Successfully navigated to {url}"
        except Exception as e:
            return f"Failed to navigate to {url}: {str(e)}"

    async def click_element(self, selector_type, selector_name, nth=0):
        try:
            elements = self.page.get_by_role(selector_type, name=selector_name).all()
            element = (await elements)[nth]
            await element.click()
            return f"Successfully clicked {selector_type}={selector_name} (nth={nth})"
        except Exception as e:
            return f"Failed to click {selector_type}={selector_name} (nth={nth}): {str(e)}"

    async def fill_input(self, selector_type, selector_name, value, nth=0):
        try:
            elements = self.page.get_by_role(selector_type, name=selector_name).all()
            element = (await elements)[nth]
            await element.fill(value)
            return f"Successfully filled {selector_type}={selector_name} (nth={nth}) with {value}"
        except Exception as e:
            return f"Failed to fill {selector_type}={selector_name} (nth={nth}): {str(e)}"

    async def press_key(self, key):
        try:
            await self.page.keyboard.press(key)
            return True, f"Successfully pressed {key}"
        except Exception as e:
            return False, f"Failed to press {key}: {str(e)}"

    async def take_screenshot(self, path):
        try:
            await self.page.screenshot(path=path)
            return True, f"Successfully saved screenshot to {path}"
        except Exception as e:
            return False, f"Failed to take screenshot: {str(e)}"

    async def wait_for_load_state(self, state='networkidle'):
        try:
            await self.page.wait_for_load_state(state)
            return True, f"Successfully waited for {state}"
        except Exception as e:
            return False, f"Failed to wait for {state}: {str(e)}"

    async def close(self):
        try:
            await self.context.close()
            await self.browser.close()
            return True, "Successfully closed browser"
        except Exception as e:
            return False, f"Failed to close browser: {str(e)}"