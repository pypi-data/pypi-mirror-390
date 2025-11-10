from abc import ABC, abstractmethod

class State(ABC):
    """
    Abstract Base Class for all game states.
    All concrete game states (MenuState, PlayState, etc.) must inherit from this.
    """
    def __init__(self, manager):
        self.manager = manager

    @abstractmethod
    def startup(self, data=None):
        """Called when the state is first entered/started."""
        pass

    @abstractmethod
    def cleanup(self):
        """Called when the state is about to be exited/popped."""
        pass

    @abstractmethod
    def handle_input(self, event):
        """Handles user input and events specific to this state."""
        pass

    @abstractmethod
    def update(self, dt):
        """Updates the game logic for this state (time delta 'dt')."""
        pass

    @abstractmethod
    def draw(self, screen):
        """Renders the game state to the screen."""
        pass

class StateManager:
    """
    Manages the stack of active game states.
    Allows pushing, popping, and switching states.
    """
    def __init__(self):
        # The state stack. The top element is the currently active state.
        self._state_stack = []

    def get_active_state(self):
        """Returns the currently active state or None if the stack is empty."""
        if self._state_stack:
            return self._state_stack[-1]
        return None

    def push_state(self, new_state_class, data=None):
        """
        Pushes a new state onto the stack and calls its startup method.
        'new_state_class' should be a class inheriting from State.
        """
        new_state = new_state_class(self)
        new_state.startup(data)
        self._state_stack.append(new_state)

    def pop_state(self):
        """
        Removes the active state from the stack and calls its cleanup method.
        """
        if self._state_stack:
            old_state = self._state_stack.pop()
            old_state.cleanup()

    def switch_state(self, new_state_class, data=None):
        """
        Replaces the current state with a new one. Equivalent to pop then push.
        """
        self.pop_state()
        self.push_state(new_state_class, data)

    def update(self, dt):
        """Calls update on the active state."""
        state = self.get_active_state()
        if state:
            state.update(dt)

    def draw(self, screen):
        """Calls draw on the active state."""
        state = self.get_active_state()
        if state:
            state.draw(screen)

    def handle_input(self, event):
        """Calls handle_input on the active state."""
        state = self.get_active_state()
        if state:
            state.handle_input(event)