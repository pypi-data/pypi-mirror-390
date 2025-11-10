# simple-gamestates

A simple, abstract, and robust **State Machine Manager** designed for modular game development in Python (e.g., Pygame, Arcade).

This library helps organize your game logic by separating different game phases (Menu, Level 1, Pause Screen, Game Over) into distinct, manageable `State` objects.

## Features

* **Stack-based Management:** Easily pause a state (e.g., main game) and push a new state on top (e.g., pause menu), and seamlessly return when popped.
* **Abstract State Interface:** Enforces clear methods (`startup`, `cleanup`, `update`, `draw`, `handle_input`) for structured code.
* **Framework Agnostic:** Designed to integrate with any Python game framework or engine.

## Installation

```bash
pip install simple-gamestates
```

## Usage Example

```python
from pystatemachine.manager import State, StateManager

class MenuState(State):
    def startup(self, data=None):
        print("Menu loaded!")
    
    def update(self, dt):
        # Handle menu animations
        pass
    
    def draw(self, screen):
        # Draw menu background
        pass
        
    def cleanup(self):
        print("Menu exited.")

manager = StateManager()
manager.push_state(MenuState)

# In your main loop:
# manager.update(dt)
# manager.draw(screen)
```

## License

MIT License
