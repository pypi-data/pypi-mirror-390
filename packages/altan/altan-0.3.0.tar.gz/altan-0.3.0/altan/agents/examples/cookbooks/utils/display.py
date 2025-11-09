"""Rich console output utilities for SDK cookbooks."""

from typing import Any, Dict, Optional
from datetime import datetime


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def print_header(title: str, width: int = 80) -> None:
    """Print a major section header with double-line border."""
    border = "═" * width
    print(f"\n{Colors.BOLD}{Colors.CYAN}{border}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}📚 {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{border}{Colors.RESET}\n")


def print_section(title: str, width: int = 80) -> None:
    """Print a section divider."""
    border = "─" * width
    print(f"\n{Colors.BOLD}{Colors.BLUE}{border}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{border}{Colors.RESET}\n")


def print_step(step_num: int, description: str) -> None:
    """Print a numbered step."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}Step {step_num}:{Colors.RESET} {description}")


def print_message(role: str, content: str, agent_name: Optional[str] = None, indent: int = 0) -> None:
    """Print a formatted chat message."""
    prefix = "  " * indent
    
    # Role-specific formatting
    if role == "user":
        icon = "👤"
        color = Colors.BRIGHT_GREEN
        label = "User"
    elif role == "assistant":
        icon = "🤖"
        color = Colors.BRIGHT_BLUE
        label = f"Assistant ({agent_name})" if agent_name else "Assistant"
    elif role == "system":
        icon = "⚙️"
        color = Colors.BRIGHT_YELLOW
        label = "System"
    else:
        icon = "💬"
        color = Colors.WHITE
        label = role.capitalize()
    
    print(f"{prefix}{color}{icon} {label}:{Colors.RESET}")
    
    # Print content with indentation
    for line in content.split("\n"):
        print(f"{prefix}  {line}")
    print()


def print_event(event_type: str, data: Optional[Dict[str, Any]] = None, indent: int = 1) -> None:
    """Print a streaming event."""
    prefix = "  " * indent
    
    # Event-specific formatting
    event_colors = {
        "response.started": (Colors.BRIGHT_GREEN, "🚀"),
        "response.completed": (Colors.BRIGHT_GREEN, "✅"),
        "response.failed": (Colors.BRIGHT_RED, "❌"),
        "response.stopped": (Colors.YELLOW, "🛑"),
        "message_part.added": (Colors.CYAN, "➕"),
        "message_part.updated": (Colors.BLUE, "📝"),
        "message_part.completed": (Colors.GREEN, "✓"),
    }
    
    color, icon = event_colors.get(event_type, (Colors.WHITE, "📦"))
    
    print(f"{prefix}{color}{icon} {event_type}{Colors.RESET}", end="")
    
    # Print relevant data fields
    if data:
        details = []
        if "id" in data:
            details.append(f"id={data['id'][:8]}...")
        if "delta" in data and data["delta"]:
            delta_preview = str(data["delta"])[:30].replace("\n", "\\n")
            details.append(f"delta=\"{delta_preview}...\"")
        if "type" in data and event_type == "message_part.added":
            details.append(f"type={data['type']}")
        
        if details:
            print(f" {Colors.DIM}({', '.join(details)}){Colors.RESET}")
        else:
            print()
    else:
        print()


def print_agent_action(agent_name: str, action: str, details: Optional[str] = None) -> None:
    """Print an agent action."""
    print(f"{Colors.BRIGHT_MAGENTA}🤖 {agent_name}:{Colors.RESET} {action}")
    if details:
        print(f"   {Colors.DIM}{details}{Colors.RESET}")


def print_success(message: str, indent: int = 0) -> None:
    """Print a success message."""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BRIGHT_GREEN}✓{Colors.RESET} {message}")


def print_error(message: str, indent: int = 0) -> None:
    """Print an error message."""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BRIGHT_RED}✗{Colors.RESET} {message}")


def print_info(message: str, indent: int = 0) -> None:
    """Print an info message."""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BRIGHT_BLUE}ℹ{Colors.RESET} {message}")


def print_warning(message: str, indent: int = 0) -> None:
    """Print a warning message."""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BRIGHT_YELLOW}⚠{Colors.RESET} {message}")


def print_stream_stats(
    duration: float,
    event_count: int,
    text_length: int = 0,
    tool_calls: int = 0,
    tokens: Optional[int] = None,
) -> None:
    """Print streaming statistics."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Stream Summary:{Colors.RESET}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Events: {event_count}")
    if text_length > 0:
        print(f"  Text length: {text_length} chars")
    if tool_calls > 0:
        print(f"  Tool calls: {tool_calls}")
    if tokens:
        print(f"  Tokens: {tokens}")


def print_divider(width: int = 80, char: str = "─") -> None:
    """Print a simple divider line."""
    print(f"{Colors.DIM}{char * width}{Colors.RESET}")


def format_timestamp() -> str:
    """Get formatted current timestamp."""
    return datetime.now().strftime("%H:%M:%S")


def print_tool_call(name: str, arguments: Dict[str, Any], indent: int = 1) -> None:
    """Print a tool call."""
    prefix = "  " * indent
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in arguments.items())
    print(f"{prefix}{Colors.YELLOW}🔧 Tool call:{Colors.RESET} {name}({args_str})")


def print_tool_result(name: str, result: Any, indent: int = 1) -> None:
    """Print a tool result."""
    prefix = "  " * indent
    result_preview = str(result)[:100]
    print(f"{prefix}{Colors.GREEN}🔧 Tool result:{Colors.RESET} {name} → {result_preview}")

