"""
Framework Registry for multi-framework support.

This module provides a central registry of all supported agent frameworks
and their corresponding adapters. The registry allows the SuperOptiX CLI
to dynamically route compilation and optimization requests to the appropriate
framework-specific adapter.

Supported Frameworks:
- DSPy (current, enhanced)
- Microsoft Agent Framework
- OpenAI Agents SDK
- DeepAgent (LangGraph-based)
- CrewAI
- Google ADK
"""

from typing import Any, Dict, List, Optional, Type

from ..core.base_component import BaseComponent


class FrameworkAdapter:
    """
    Base class for framework-specific adapters.

    Each adapter is responsible for:
    1. Converting SuperSpec playbooks to framework-specific code
    2. Wrapping framework agents as BaseComponent instances
    3. Extracting optimizable variables for GEPA
    4. Generating deployable code
    """

    framework_name: str = "base"
    requires_async: bool = False

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """
        Compile SuperSpec playbook to framework-specific code.

        Args:
            playbook: Parsed SuperSpec YAML playbook
            output_path: Directory to write generated code

        Returns:
            Path to generated agent file
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement compile_from_playbook()"
        )

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """
        Create a BaseComponent instance from a playbook.

        This method wraps the framework-specific agent in a framework-agnostic
        BaseComponent interface, enabling universal optimization with GEPA.

        Args:
            playbook: Parsed SuperSpec YAML playbook
            **kwargs: Additional configuration

        Returns:
            BaseComponent instance wrapping the framework agent
        """
        raise NotImplementedError(f"{cls.__name__} must implement create_component()")

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """
        Extract the optimizable variable from the playbook.

        Different frameworks use different variable names:
        - DSPy: signature instructions
        - Microsoft: instructions
        - OpenAI: instructions
        - DeepAgent: system_prompt
        - CrewAI: role/goal/backstory
        - Google ADK: description

        Args:
            playbook: Parsed SuperSpec YAML playbook

        Returns:
            The optimizable variable (prompt/instructions/etc.)
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement get_optimizable_variable()"
        )


class DSPyFrameworkAdapter(FrameworkAdapter):
    """Adapter for DSPy framework (current implementation)."""

    framework_name = "dspy"
    requires_async = False

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to DSPy pipeline (existing implementation)."""
        # This will delegate to the existing AgentCompiler
        # We keep the current excellent DSPy workflow unchanged
        from ..compiler.agent_compiler import AgentCompiler

        compiler = AgentCompiler(playbook, output_path)
        return compiler.compile()

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping DSPy agent."""
        # This will be implemented when integrating with universal GEPA
        raise NotImplementedError("DSPy BaseComponent integration pending")

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract DSPy signature instructions."""
        return playbook.get("persona", {}).get("instructions", "")


class MicrosoftFrameworkAdapter(FrameworkAdapter):
    """Adapter for Microsoft Agent Framework."""

    framework_name = "microsoft"
    requires_async = True

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to Microsoft Agent Framework code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("microsoft_agent_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_microsoft_pipeline" in filename:
            agent_name = filename.replace("_microsoft_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")
        
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping Microsoft agent."""
        # This will be used by Universal GEPA optimizer
        # For now, we need to compile and import the generated module
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        
        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        
        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_microsoft_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Microsoft agent instructions."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class OpenAIFrameworkAdapter(FrameworkAdapter):
    """Adapter for OpenAI Agents SDK."""

    framework_name = "openai"
    requires_async = False

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to OpenAI Agents SDK code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("openai_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_openai_pipeline" in filename:
            agent_name = filename.replace("_openai_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")
        
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping OpenAI agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        
        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        
        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_openai_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract OpenAI agent instructions."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class DeepAgentsFrameworkAdapter(FrameworkAdapter):
    """Adapter for DeepAgents (LangGraph-based)."""

    framework_name = "deepagents"
    requires_async = True

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to DeepAgent code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("deepagents_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        # This ensures the class name matches what the runner expects
        # e.g., "code_reviewer_deepagents_pipeline.py" → "code_reviewer"
        output_file = Path(output_path)
        filename = output_file.stem  # e.g., "code_reviewer_deepagents_pipeline"
        # Remove framework suffix if present
        if "_deepagents_pipeline" in filename:
            agent_name = filename.replace("_deepagents_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")
        
        # Fallback to playbook metadata if we can't extract from filename
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping DeepAgents agent."""
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        
        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        
        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_deepagents_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract DeepAgent system_prompt."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class CrewAIFrameworkAdapter(FrameworkAdapter):
    """Adapter for CrewAI framework."""

    framework_name = "crewai"
    requires_async = False

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to CrewAI code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("crewai_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_crewai_pipeline" in filename:
            agent_name = filename.replace("_crewai_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")
        
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping CrewAI agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        
        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        
        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_crewai_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract CrewAI role/goal/backstory."""
        persona = playbook.get("spec", {}).get("persona", {})
        # CrewAI uses role + goal + backstory pattern
        role = persona.get("role", "")
        goal = persona.get("goal", "")
        backstory = persona.get("backstory", "")
        return f"Role: {role}\nGoal: {goal}\nBackstory: {backstory}"


class GoogleADKFrameworkAdapter(FrameworkAdapter):
    """Adapter for Google Agent Development Kit (ADK)."""

    framework_name = "google-adk"
    requires_async = False

    @classmethod
    def compile_from_playbook(
        cls, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """Compile SuperSpec to Google ADK code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("google_adk_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_google_adk_pipeline" in filename:
            agent_name = filename.replace("_google_adk_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")
        
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(
        cls, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """Create BaseComponent wrapping Google ADK agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        
        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        
        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_google_adk_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Google ADK instruction."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class FrameworkRegistry:
    """
    Central registry of all supported agent frameworks.

    This registry provides:
    1. Discovery: List all available frameworks
    2. Routing: Get the appropriate adapter for a framework
    3. Validation: Check if a framework is supported
    4. Metadata: Framework capabilities and requirements
    """

    _adapters: Dict[str, Type[FrameworkAdapter]] = {
        "dspy": DSPyFrameworkAdapter,
        "microsoft": MicrosoftFrameworkAdapter,
        "openai": OpenAIFrameworkAdapter,
        "deepagents": DeepAgentsFrameworkAdapter,
        "crewai": CrewAIFrameworkAdapter,
        "google-adk": GoogleADKFrameworkAdapter,
    }

    @classmethod
    def get_adapter(cls, framework: str) -> Type[FrameworkAdapter]:
        """
        Get the adapter class for the specified framework.

        Args:
            framework: Framework name (e.g., "dspy", "crewai", "openai")

        Returns:
            FrameworkAdapter subclass for the framework

        Raises:
            ValueError: If framework is not supported
        """
        framework = framework.lower()
        if framework not in cls._adapters:
            available = ", ".join(cls.list_frameworks())
            raise ValueError(
                f"Unsupported framework: '{framework}'. Available: {available}"
            )
        return cls._adapters[framework]

    @classmethod
    def list_frameworks(cls) -> List[str]:
        """
        List all supported framework names.

        Returns:
            List of framework names
        """
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, framework: str) -> bool:
        """
        Check if a framework is supported.

        Args:
            framework: Framework name to check

        Returns:
            True if framework is supported
        """
        return framework.lower() in cls._adapters

    @classmethod
    def get_framework_info(cls, framework: str) -> Dict[str, Any]:
        """
        Get metadata about a framework.

        Args:
            framework: Framework name

        Returns:
            Dict with framework metadata (name, async requirement, etc.)
        """
        adapter = cls.get_adapter(framework)
        return {
            "name": adapter.framework_name,
            "requires_async": adapter.requires_async,
            "implemented": adapter.compile_from_playbook
            != FrameworkAdapter.compile_from_playbook,
        }

    @classmethod
    def compile_agent(
        cls, framework: str, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """
        Compile an agent playbook using the specified framework.

        This is the main entry point for multi-framework compilation.

        Args:
            framework: Target framework name
            playbook: Parsed SuperSpec YAML playbook
            output_path: Directory to write generated code

        Returns:
            Path to generated agent file
        """
        adapter = cls.get_adapter(framework)
        return adapter.compile_from_playbook(playbook, output_path)

    @classmethod
    def create_component(
        cls, framework: str, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """
        Create a BaseComponent from a playbook using the specified framework.

        This is used by the universal GEPA optimizer.

        Args:
            framework: Target framework name
            playbook: Parsed SuperSpec YAML playbook
            **kwargs: Additional configuration

        Returns:
            BaseComponent wrapping the framework agent
        """
        adapter = cls.get_adapter(framework)
        return adapter.create_component(playbook, **kwargs)

    @classmethod
    def register_adapter(cls, framework: str, adapter: Type[FrameworkAdapter]) -> None:
        """
        Register a custom framework adapter.

        This allows users to add support for additional frameworks.

        Args:
            framework: Framework name
            adapter: FrameworkAdapter subclass
        """
        cls._adapters[framework.lower()] = adapter
