"""
Dependency Injection Container for the Personal AI Trainer application.

This module provides a lightweight dependency injection container that handles
registration, resolution, and lifecycle management of dependencies.
"""

import inspect
from typing import Any, Dict, Callable, Type, TypeVar, Optional, Union, get_type_hints

T = TypeVar('T')


class DIContainer:
    """
    Lightweight dependency injection container for managing service dependencies.
    
    Provides registration, resolution, and lifecycle management of dependencies.
    
    Attributes:
        _services (Dict): Dictionary mapping interfaces to implementation details.
        _instances (Dict): Dictionary of singleton instances.
    """
    
    def __init__(self):
        """
        Initialize an empty dependency injection container.
        """
        self._services = {}
        self._instances = {}
        
    def register(self, interface: Any, implementation: Any, singleton: bool = True) -> 'DIContainer':
        """
        Register a service with the container.
        
        Args:
            interface: The interface or key for the service.
            implementation: The implementation class or factory function.
            singleton (bool): Whether to treat this as a singleton. Defaults to True.
                
        Returns:
            DIContainer: The container instance for method chaining.
            
        Example:
            ```python
            container = DIContainer()
            container.register(Database, PostgresDatabase)
            container.register('config', lambda c: load_config())
            ```
        """
        self._services[interface] = {
            'implementation': implementation,
            'singleton': singleton
        }
        return self
        
    def resolve(self, interface: Any) -> Any:
        """
        Resolve a service from the container.
        
        Args:
            interface: The interface or key for the service to resolve.
                
        Returns:
            Any: The resolved service instance.
            
        Raises:
            KeyError: If the requested service is not registered.
            
        Example:
            ```python
            db = container.resolve(Database)
            config = container.resolve('config')
            ```
        """
        if interface not in self._services:
            raise KeyError(f"Service {interface} not registered")
            
        if self._services[interface]['singleton']:
            if interface not in self._instances:
                self._instances[interface] = self._create_instance(interface)
            return self._instances[interface]
        else:
            return self._create_instance(interface)
            
    def _create_instance(self, interface: Any) -> Any:
        """
        Create an instance of the implementation for the given interface.
        
        Args:
            interface: The interface to create an implementation for.
                
        Returns:
            Any: The created instance.
            
        Raises:
            ValueError: If the implementation cannot be instantiated.
        """
        implementation = self._services[interface]['implementation']
        
        # If it's a factory function (callable but not a class)
        if callable(implementation) and not isinstance(implementation, type):
            return implementation(self)
            
        # If it's a class, try to inject dependencies
        try:
            # Try to create instance without arguments
            return implementation()
        except TypeError:
            # If that fails, inspect the constructor and try to resolve dependencies
            try:
                if not hasattr(implementation, '__init__'):
                    raise ValueError(f"Cannot instantiate {implementation}")
                    
                # Get constructor signature
                sig = inspect.signature(implementation.__init__)
                
                # Skip self parameter
                params = list(sig.parameters.values())[1:]
                
                # Try to resolve each parameter
                args = []
                for param in params:
                    # If parameter has a default value and no annotation, use default
                    if param.default is not inspect.Parameter.empty and param.annotation is inspect.Parameter.empty:
                        continue
                        
                    # If parameter has an annotation, try to resolve it
                    if param.annotation is not inspect.Parameter.empty:
                        try:
                            args.append(self.resolve(param.annotation))
                            continue
                        except KeyError:
                            # If we can't resolve it and it has a default, use default
                            if param.default is not inspect.Parameter.empty:
                                continue
                            # Otherwise, raise error
                            raise ValueError(f"Cannot resolve parameter {param.name} of type {param.annotation}")
                            
                    # If we get here, we can't resolve the parameter
                    raise ValueError(f"Cannot resolve parameter {param.name}")
                    
                # Create instance with resolved dependencies
                return implementation(*args)
            except Exception as e:
                # If all else fails, try passing the container itself
                try:
                    return implementation(self)
                except Exception:
                    raise ValueError(f"Cannot instantiate {implementation}: {e}")
                    
    def clear(self) -> None:
        """
        Clear all singleton instances, forcing them to be recreated on next resolve.
        
        Example:
            ```python
            container.clear()  # All singletons will be recreated on next resolve
            ```
        """
        self._instances.clear()