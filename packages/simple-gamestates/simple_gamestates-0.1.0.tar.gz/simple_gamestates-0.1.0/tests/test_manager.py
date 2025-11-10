import unittest.mock
import pytest
from src.pystatemachine.manager import State, StateManager

# Test için soyut State sınıfından türetilmiş somut bir State sınıfı oluşturalım.
# Mock'ları kullanarak, startup, cleanup vb. metodların çağrılıp çağrılmadığını kontrol edeceğiz.
class MockState(State):
    """A concrete State class for testing purposes."""
    def startup(self, data=None):
        pass # Bu metot testler sırasında mocklanacaktır

    def cleanup(self):
        pass # Bu metot testler sırasında mocklanacaktır

    def handle_input(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

# Ana Test Sınıfı
class TestStateManager:

    @pytest.fixture
    def manager(self):
        """Provides a fresh StateManager instance for each test."""
        return StateManager()

    @pytest.fixture
    def MockStateClass(self):
        """Provides a MockState class with mocked methods."""
        # unittest.mock.MagicMock kullanarak State metodlarını mockluyoruz
        MockState.startup = unittest.mock.MagicMock()
        MockState.cleanup = unittest.mock.MagicMock()
        MockState.handle_input = unittest.mock.MagicMock()
        MockState.update = unittest.mock.MagicMock()
        MockState.draw = unittest.mock.MagicMock()
        return MockState

    def test_initialization(self, manager):
        """Test the manager starts with an empty state stack."""
        assert manager.get_active_state() is None

    def test_push_state(self, manager, MockStateClass):
        """Test pushing a new state."""
        manager.push_state(MockStateClass)

        active_state = manager.get_active_state()
        
        # 1. Doğru sınıfın yığına eklendiğini kontrol et
        assert isinstance(active_state, MockStateClass)
        
        # 2. Yeni durumun startup metodunun çağrıldığını kontrol et
        active_state.startup.assert_called_once()
        
        # 3. Manager'ın kendisine referans verdiğini kontrol et
        assert active_state.manager is manager

    def test_pop_state(self, manager, MockStateClass):
        """Test popping a state and checking cleanup."""
        manager.push_state(MockStateClass)
        active_state = manager.get_active_state()

        manager.pop_state()
        
        # 1. Yığının boşaldığını kontrol et
        assert manager.get_active_state() is None
        
        # 2. Çıkarılan durumun cleanup metodunun çağrıldığını kontrol et
        active_state.cleanup.assert_called_once()

    def test_switch_state(self, manager, MockStateClass):
        """Test switching from StateA to StateB."""
        class StateA(MockStateClass):
            pass
        
        class StateB(MockStateClass):
            pass

        # StateA'yı push et
        manager.push_state(StateA)
        state_a_instance = manager.get_active_state()

        # StateA tarafından çağrılan startup sayısını temizle
        # Bu, MockState sınıfındaki paylaşılan mock'u temizler.
        MockStateClass.startup.reset_mock() 

        # StateB'ye switch et (StateA'yı pop, StateB'yi push eder)
        manager.switch_state(StateB)
        state_b_instance = manager.get_active_state()
        
        # 1. StateB'nin aktif olduğunu kontrol et
        assert isinstance(state_b_instance, StateB)
        
        # 2. Önceki durumun (StateA) cleanup metodunun çağrıldığını kontrol et
        # NOT: cleanup metodu sıfırlanmadı, bu yüzden hala çağrıldığını kontrol edebiliriz.
        state_a_instance.cleanup.assert_called_once()
        
        # 3. Yeni durumun (StateB) startup metodunun çağrıldığını kontrol et (Bu, reset'ten sonra 1. çağrı olmalı)
        state_b_instance.startup.assert_called_once()

    def test_delegation(self, manager, MockStateClass):
        """Test update, draw, and handle_input are delegated to the active state."""
        manager.push_state(MockStateClass)
        active_state = manager.get_active_state()
        
        # Simüle edilmiş çağrılar
        manager.update(1.0/60.0)
        manager.draw(None)
        manager.handle_input('key_press')
        
        # Metodların çağrılıp çağrılmadığını kontrol et
        active_state.update.assert_called_once()
        active_state.draw.assert_called_once()
        active_state.handle_input.assert_called_once()