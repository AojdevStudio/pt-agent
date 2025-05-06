"""
Agent communication utilities for Personal AI Training Agent.

Handles agency structure setup, agent registration, message passing, and response handling.

Author: Roo Mid
"""

from typing import Any, Dict, List, Optional, Callable, Union
from agency_swarm.agency.agency import Agency
from agency_swarm.agents.agent import Agent

class CommunicationManager:
    """
    Manages agent communication and agency structure.
    """

    def __init__(
        self,
        agency_chart: List[Dict[str, Any]],
        shared_instructions: str = "",
        shared_files: Optional[Union[str, List[str]]] = None,
        **kwargs
    ):
        """
        Initialize the CommunicationManager and set up the agency.

        Args:
            agency_chart (List[Dict[str, Any]]): Structure defining agent hierarchy and communication.
            shared_instructions (str): Shared instructions for all agents.
            shared_files (Optional[Union[str, List[str]]]): Shared files for all agents.
            **kwargs: Additional parameters for Agency.
        """
        self.agency = Agency(
            agency_chart=agency_chart,
            shared_instructions=shared_instructions,
            shared_files=shared_files,
            **kwargs
        )

    def send_message(
        self,
        message: str,
        recipient_agent: Optional[Agent] = None,
        message_files: Optional[List[str]] = None,
        additional_instructions: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
        tool_choice: Optional[dict] = None,
        verbose: bool = False,
        response_format: Optional[dict] = None,
    ) -> str:
        """
        Send a message to an agent and get the response.

        Args:
            message (str): The message to send.
            recipient_agent (Optional[Agent]): The agent to receive the message.
            message_files (Optional[List[str]]): Files to send with the message.
            additional_instructions (Optional[str]): Extra instructions.
            attachments (Optional[List[dict]]): Attachments for the message.
            tool_choice (Optional[dict]): Tool choice for the agent.
            verbose (bool): Whether to print intermediary messages.
            response_format (Optional[dict]): Response format.

        Returns:
            str: The agent's response.
        """
        return self.agency.get_completion(
            message=message,
            recipient_agent=recipient_agent,
            message_files=message_files,
            additional_instructions=additional_instructions,
            attachments=attachments,
            tool_choice=tool_choice,
            verbose=verbose,
            response_format=response_format,
        )

    def broadcast_message(
        self,
        message: str,
        agent_names: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Broadcast a message to multiple agents and collect responses.

        Args:
            message (str): The message to broadcast.
            agent_names (Optional[List[str]]): List of agent names to receive the message.
            **kwargs: Additional arguments for send_message.

        Returns:
            Dict[str, str]: Mapping of agent name to response.
        """
        responses = {}
        agents = (
            self.agency._get_agents_by_names(agent_names)
            if agent_names else self.agency.agents
        )
        for agent in agents:
            responses[agent.name] = self.send_message(message, recipient_agent=agent, **kwargs)
        return responses

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Retrieve an agent by name.

        Args:
            name (str): The agent's name.

        Returns:
            Optional[Agent]: The agent instance, or None if not found.
        """
        return self.agency._get_agent_by_name(name)

    def get_agency_structure(self) -> List[str]:
        """
        Get the names of all agents in the agency.

        Returns:
            List[str]: List of agent names.
        """
        return self.agency._get_agent_names()