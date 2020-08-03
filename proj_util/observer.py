from abc import ABCMeta, abstractmethod

class Observer( metaclass = ABCMeta ):
    @abstractmethod
    def model_is_changed( self ):
        pass