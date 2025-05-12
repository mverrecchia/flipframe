import importlib
import traceback

class PageManager:
    def __init__(self, display_adapter):
        self.enabled = True
        self.display_adapter = display_adapter
        self.pages = {}  # page_id -> page_class dict
        self.page_metadata = {}  # page_id -> metadata dict
        self.current_page_id = None
        self.current_page = None
        self.page_history = []
        self.max_history = 10
    
    def register_page(self, page_id, page_class, metadata=None):
        if page_id in self.pages:
            print(f"Warning: Overwriting existing page with ID '{page_id}'")
        
        self.pages[page_id] = page_class
        self.page_metadata[page_id] = metadata or {}
        return True
    
    def register_pages_from_module(self, module_name):
        try:
            module = importlib.import_module(module_name)
            
            if not hasattr(module, 'PAGES'):
                print(f"Module '{module_name}' has no PAGES attribute")
                return False
            
            pages_dict = getattr(module, 'PAGES')
            
            print(f"Found {len(pages_dict)} pages in module '{module_name}'")
            
            # Register each page
            for page_id, page_info in pages_dict.items():
                try:
                    if isinstance(page_info, tuple) and len(page_info) >= 2:
                        page_class, metadata = page_info
                        self.register_page(page_id, page_class, metadata)
                    else:
                        self.register_page(page_id, page_info)
                except Exception as e:
                    print(f"Error registering page '{page_id}': {e}")
            
            return len(self.pages) > 0
            
        except Exception as e:
            print(f"Error importing module '{module_name}': {e}")
            traceback.print_exc()
            return False
    
    def get_page_ids(self):
        return list(self.pages.keys())
    
    def get_page_metadata(self, page_id):
        return self.page_metadata.get(page_id, {})
    
    def navigate_to(self, page_id):
        if page_id not in self.pages:
            print(f"Error: Page with ID '{page_id}' not found")
            return False
        
        if self.current_page_id is not None:
            self.page_history.append(self.current_page_id)
            if len(self.page_history) > self.max_history:
                self.page_history.pop(0)
        
        page_class = self.pages[page_id]
        
        if self.current_page is not None:
            try:
                self.current_page.cleanup()
            except Exception as e:
                print(f"Error cleaning up page '{self.current_page_id}': {e}")
        
        try:
            self.current_page = page_class(self.display_adapter)
            self.current_page_id = page_id
            self.current_page.initialize()
            return True
        except Exception as e:
            print(f"Error initializing page '{page_id}': {e}")
            traceback.print_exc()
            self.current_page = None
            self.current_page_id = None
            return False
    
    def next_page(self):
        page_ids = self.get_page_ids()
        
        if not page_ids:
            return False
        
        # if no current page, navigate to the first page
        if self.current_page_id is None:
            return self.navigate_to(page_ids[0])
        
        try:
            current_index = page_ids.index(self.current_page_id)
        except ValueError:
            current_index = -1
        
        next_index = (current_index + 1) % len(page_ids)
        return self.navigate_to(page_ids[next_index])
    
    def previous_page(self):
        page_ids = self.get_page_ids()
        
        if not page_ids:
            return False
        
        if self.current_page_id is None:
            return self.navigate_to(page_ids[-1])
        
        try:
            current_index = page_ids.index(self.current_page_id)
        except ValueError:
            current_index = 0
        
        prev_index = (current_index - 1) % len(page_ids)
        return self.navigate_to(page_ids[prev_index])
    
    def back(self):
        if not self.page_history:
            return False
        
        # pop the last page from history
        previous_page_id = self.page_history.pop()
        
        if previous_page_id in self.pages:
            page_class = self.pages[previous_page_id]
            
            # cleanup current page if it exists
            if self.current_page is not None:
                try:
                    self.current_page.cleanup()
                except Exception as e:
                    print(f"Error cleaning up page '{self.current_page_id}': {e}")
            
            # create the new page
            try:
                self.current_page = page_class(self.display_adapter)
                self.current_page_id = previous_page_id
                self.current_page.initialize()
                return True
            except Exception as e:
                print(f"Error initializing page '{previous_page_id}': {e}")
                self.current_page = None
                self.current_page_id = None
                return False
        
        return False
    
    def handle_slider_change(self, value):
        if self.current_page is not None and hasattr(self.current_page, 'handle_slider_change'):
            try:
                self.current_page.handle_slider_change(value)
                return True
            except Exception as e:
                print(f"Error handling slider change on page '{self.current_page_id}': {e}")
                traceback.print_exc()
        return False
    
    def update(self, camera_frame=None, face_landmarks=None, gestures=None):
        if self.current_page is None:
            return False

        try:
            if self.enabled:
                self.current_page.update(camera_frame, face_landmarks, gestures)
            else:
                self.current_page.clear_frame()
                self.current_page.render()
            return True
        except Exception as e:
            print(f"Error updating page '{self.current_page_id}': {e}")
            traceback.print_exc()
            return False
    
    def render(self):
        if self.current_page is None:
            return None
        
        try:
            return self.current_page.render()
        except Exception as e:
            print(f"Error rendering page '{self.current_page_id}': {e}")
            traceback.print_exc()
            return None
    
    def cleanup(self):
        if self.current_page is not None:
            try:
                self.current_page.cleanup()
            except Exception as e:
                print(f"Error cleaning up page '{self.current_page_id}': {e}")
    