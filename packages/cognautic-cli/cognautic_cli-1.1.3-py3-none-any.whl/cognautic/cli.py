"""
Main CLI interface for Cognautic
"""

import click
import asyncio
import logging
import os
import readline
import signal
from pathlib import Path
import sys
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Suppress verbose logging from Google AI and other libraries
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GRPC_TRACE'] = ''
os.environ['GLOG_minloglevel'] = '3'  # Suppress all Google logging
os.environ['GLOG_logtostderr'] = '0'  # Don't log to stderr
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
os.environ['ABSL_LOGGING_VERBOSITY'] = '3'  # Suppress ABSL logs

# Redirect stderr to suppress C++ library logs
import sys
import io

# Create a custom stderr that filters out Google AI noise
class FilteredStderr:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = ""
    
    def write(self, text):
        # Filter out Google AI error messages
        if any(pattern in text for pattern in [
            'ALTS creds ignored',
            'plugin_credentials.cc',
            'validate_metadata_from_plugin',
            'Plugin added invalid metadata',
            'All log messages before absl::InitializeLog',
            'INTERNAL:Illegal header value'
        ]):
            return
        self.original_stderr.write(text)
    
    def flush(self):
        self.original_stderr.flush()
    
    def isatty(self):
        return self.original_stderr.isatty()

# Install the filtered stderr
sys.stderr = FilteredStderr(sys.stderr)

logging.getLogger('google').setLevel(logging.CRITICAL)
logging.getLogger('google.generativeai').setLevel(logging.CRITICAL)
logging.getLogger('websockets').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('grpc').setLevel(logging.CRITICAL)

# Set root logger to WARNING to suppress debug messages
logging.basicConfig(level=logging.WARNING)

from .config import ConfigManager
from .ai_engine import AIEngine
from .websocket_server import WebSocketServer
from .memory import MemoryManager
from .rules import RulesManager

console = Console()

# Global flag to stop AI response
stop_response = False

def signal_handler(signum, frame):
    """Handle Ctrl+X (SIGQUIT) to stop AI response"""
    global stop_response
    stop_response = True




@click.group(invoke_without_command=True)
@click.version_option(version="1.1.3", prog_name="Cognautic CLI")
@click.pass_context
def main(ctx):
    """Cognautic CLI - AI-powered development assistant"""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, start interactive chat
        ctx.invoke(chat)

@main.command()
@click.option('--provider', help='AI provider to configure')
@click.option('--api-key', help='API key for the provider')
@click.option('--interactive', is_flag=True, help='Interactive setup mode')
def setup(provider, api_key, interactive):
    """Initialize Cognautic CLI and configure API keys"""
    console.print(Panel.fit("🚀 Cognautic CLI Setup", style="bold blue"))
    
    config_manager = ConfigManager()
    
    if interactive:
        config_manager.interactive_setup()
    elif provider and api_key:
        config_manager.set_api_key(provider, api_key)
        console.print(f"SUCCESS: API key for {provider} configured successfully", style="green")
    else:
        console.print("ERROR: Please provide --provider and --api-key, or use --interactive", style="red")

@main.command()
@click.option('--provider', help='AI provider to use')
@click.option('--model', help='Specific model to use')
@click.option('--project-path', type=click.Path(exists=True), help='Project path to work with')
@click.option('--websocket-port', default=8765, help='WebSocket server port')
@click.option('--session', help='Session ID to continue')
def chat(provider, model, project_path, websocket_port, session):
    """Start interactive chat session with AI agent"""
    ascii_art = """
 ██████╗ ██████╗  ██████╗ ███╗   ██╗ █████╗ ██╗   ██╗████████╗██╗ ██████╗
██╔════╝██╔═══██╗██╔════╝ ████╗  ██║██╔══██╗██║   ██║╚══██╔══╝██║██╔════╝
██║     ██║   ██║██║  ███╗██╔██╗ ██║███████║██║   ██║   ██║   ██║██║     
██║     ██║   ██║██║   ██║██║╚██╗██║██╔══██║██║   ██║   ██║   ██║██║     
╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝
"""
    console.print(ascii_art, style="bold green")
    
    # Handle Sentinel objects from Click
    if not isinstance(provider, str):
        provider = None
    if not isinstance(model, str):
        model = None
    if not isinstance(project_path, (str, type(None))):
        project_path = None
    if not isinstance(session, str):
        session = None
    
    config_manager = ConfigManager()
    memory_manager = MemoryManager()
    
    # Check if any providers are configured
    available_providers = config_manager.list_providers()
    if not available_providers:
        console.print("🔧 No API keys configured. Let's set up Cognautic CLI first!", style="yellow")
        config_manager.interactive_setup()
        available_providers = config_manager.list_providers()
        if not available_providers:
            console.print("ERROR: Setup cancelled. Cannot start chat without API keys.", style="red")
            return
    
    # Handle session loading
    if session:
        if memory_manager.load_session(session):
            current_session = memory_manager.get_current_session()
            if not provider:
                provider = current_session.provider
            if not model:
                model = current_session.model
            if not project_path:
                project_path = current_session.workspace
        else:
            return
    
    # Use provided provider or last used provider or default
    if not provider or not isinstance(provider, str):
        provider = config_manager.get_config_value('last_provider') or config_manager.get_config_value('default_provider') or available_providers[0]
    
    if not config_manager.has_api_key(provider):
        console.print(f"ERROR: No API key found for {provider}. Available providers: {', '.join(available_providers)}", style="red")
        return
    
    # Load saved model for the provider if no model was specified
    if not model or not isinstance(model, str):
        saved_model = config_manager.get_provider_model(provider)
        if saved_model:
            model = saved_model
    
    ai_engine = AIEngine(config_manager)
    
    # Start WebSocket server in background
    websocket_server = WebSocketServer(ai_engine, port=websocket_port)
    
    async def run_chat():
        global stop_response
        
        # Set up Ctrl+X signal handler (SIGQUIT)
        signal.signal(signal.SIGQUIT, signal_handler)
        
        # Start WebSocket server
        server_task = asyncio.create_task(websocket_server.start())
        
        try:
            console.print("INFO: Type '/help' for commands, 'exit' to quit")
            console.print("INFO: Press Shift+Tab to toggle Terminal mode")
            if project_path:
                console.print(f"DIR: Working in: {project_path}")
            
            # Only show session info if continuing an existing session
            if memory_manager.get_current_session():
                current_session = memory_manager.get_current_session()
                console.print(f"SESSION: Continuing session: {current_session.session_id} - {current_session.title}")
                # Show recent conversation history
                history = memory_manager.get_conversation_history(limit=3)
                if history:
                    console.print("\n[dim]Recent conversation:[/dim]")
                    for msg in history[-3:]:
                        role_color = "cyan" if msg.role == "user" else "magenta"
                        console.print(f"[{role_color}]{msg.role.title()}:[/{role_color}] {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")
            
            console.print("-" * 50)
            
            # Set workspace - use provided project_path or current working directory
            current_workspace = project_path or os.getcwd()
            # Load saved provider/model from config if not specified
            saved_provider = config_manager.get_config_value('last_provider')
            saved_model = config_manager.get_config_value('last_model')
            
            current_model = model or saved_model  # Track current model in this scope
            current_provider = provider or saved_provider or 'openai'  # Track current provider in this scope
            session_created = False  # Track if session has been created
            
            # Store the original working directory where cognautic was run
            original_cwd = os.getcwd()
            
            # Setup readline for command history and arrow keys
            history_file = Path.home() / ".cognautic" / ".chat_history"
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                readline.read_history_file(str(history_file))
            except FileNotFoundError:
                pass
            
            # Set history length
            readline.set_history_length(1000)
            
            # Show current workspace
            console.print(f"DIR: Workspace: {current_workspace}")
            
            # Terminal mode state
            terminal_mode = [False]  # Use list to make it mutable in nested function
            
            # Setup key bindings for Shift+Tab toggle
            bindings = KeyBindings()
            
            @bindings.add('s-tab')  # Shift+Tab
            def toggle_mode(event):
                terminal_mode[0] = not terminal_mode[0]
                mode_name = ">  Terminal" if terminal_mode[0] else " Chat"
                # Clear current line and show mode switch message
                event.app.current_buffer.text = ''
                event.app.exit(result='__MODE_TOGGLE__')
            
            # Create prompt session
            session = PromptSession(key_bindings=bindings)
            
            console.print("[dim]INFO: Press Shift+Tab to toggle between Chat and Terminal modes[/dim]\n")
            
            while True:
                try:
                    # Show current workspace and mode in prompt
                    workspace_info = f" [{Path(current_workspace).name}]" if current_workspace else ""
                    mode_indicator = "> " if terminal_mode[0] else ""
                    
                    prompt_text = HTML(f'<ansibrightcyan><b>{mode_indicator}You{workspace_info}:</b></ansibrightcyan> ')
                    user_input = await session.prompt_async(prompt_text)
                    
                    # Handle mode toggle
                    if user_input == '__MODE_TOGGLE__':
                        mode_name = ">  Terminal" if terminal_mode[0] else ">  Chat"
                        console.print(f"[bold yellow]Switched to {mode_name} mode[/bold yellow]")
                        console.print("[dim]Press Shift+Tab to toggle modes[/dim]")
                        continue
                    
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    
                    # Handle terminal mode
                    if terminal_mode[0]:
                        if not user_input.strip():
                            continue
                        
                        # Execute command in terminal mode with live output
                        try:
                            # Run command with live output streaming
                            process = subprocess.Popen(
                                user_input,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                cwd=current_workspace,
                                bufsize=1,  # Line buffered
                                universal_newlines=True
                            )
                            
                            # Stream output in real-time
                            import select
                            import time
                            
                            try:
                                while True:
                                    # Check if process has finished
                                    if process.poll() is not None:
                                        # Read any remaining output
                                        remaining_stdout = process.stdout.read()
                                        remaining_stderr = process.stderr.read()
                                        if remaining_stdout:
                                            console.print(remaining_stdout, end='')
                                        if remaining_stderr:
                                            console.print(f"[red]{remaining_stderr}[/red]", end='')
                                        break
                                    
                                    # Read stdout
                                    stdout_line = process.stdout.readline()
                                    if stdout_line:
                                        console.print(stdout_line, end='')
                                    
                                    # Read stderr
                                    stderr_line = process.stderr.readline()
                                    if stderr_line:
                                        console.print(f"[red]{stderr_line}[/red]", end='')
                                    
                                    # Small sleep to prevent busy waiting
                                    if not stdout_line and not stderr_line:
                                        time.sleep(0.01)
                                
                                # Wait for process to complete
                                returncode = process.wait()
                                
                                # Show exit code if non-zero
                                if returncode != 0:
                                    console.print(f"[yellow]Exit code: {returncode}[/yellow]")
                                    
                            except KeyboardInterrupt:
                                # Handle Ctrl+C - terminate the process
                                console.print("\n[yellow]^C[/yellow]")
                                process.terminate()
                                try:
                                    process.wait(timeout=2)
                                except subprocess.TimeoutExpired:
                                    process.kill()
                                    process.wait()
                                console.print("[yellow]Process terminated[/yellow]")
                            
                        except Exception as e:
                            console.print(f"[red]Error executing command: {str(e)}[/red]")
                        
                        continue
                    
                    # Handle slash commands
                    if user_input.startswith('/'):
                        # Create context dict for slash commands
                        context = {
                            'current_workspace': current_workspace,
                            'model': current_model,
                            'provider': current_provider,
                            'memory_manager': memory_manager,
                            'original_cwd': original_cwd,
                            'config_manager': config_manager
                        }
                        result = await handle_slash_command(user_input, config_manager, ai_engine, context)
                        if result:
                            # Update local variables from context
                            old_workspace = current_workspace
                            current_workspace = context.get('current_workspace', current_workspace)
                            current_model = context.get('model', current_model)
                            current_provider = context.get('provider', current_provider)
                            
                            # If workspace changed, update the session
                            if old_workspace != current_workspace and memory_manager.get_current_session():
                                memory_manager.update_session_info(workspace=current_workspace)
                            
                            continue
                        else:
                            break
                    
                    # Create session only when user sends first actual message (not slash command)
                    if not session_created and not memory_manager.get_current_session():
                        session_id = memory_manager.create_session(
                            provider=current_provider,
                            model=current_model,
                            workspace=current_workspace
                        )
                        session_created = True
                    
                    # Add user message to memory
                    memory_manager.add_message("user", user_input)
                    
                    # Update session title if this is the first message
                    current_session = memory_manager.get_current_session()
                    if current_session and current_session.message_count == 1:
                        title = memory_manager.generate_session_title(user_input)
                        memory_manager.update_session_info(title=title)
                    
                    # Process user input with AI (including conversation history)
                    console.print(f"[dim]Processing with {current_provider}, model: {current_model or 'default'}...[/dim]")
                    
                    # Get conversation history for context
                    conversation_history = memory_manager.get_context_for_ai(limit=10)
                    
                    # Get typing speed from config (default: fast)
                    typing_speed = config_manager.get_config_value('typing_speed') or 'fast'
                    speed_map = {
                        'instant': 0,
                        'fast': 0.001,
                        'normal': 0.005,
                        'slow': 0.01
                    }
                    typing_delay = speed_map.get(typing_speed, 0.001) if isinstance(typing_speed, str) else float(typing_speed)
                    
                    # Add border before AI response
                    console.print("[bold magenta]─[/bold magenta]" * 50)
                    console.print("[bold magenta]AI:[/bold magenta] ", end="")
                    full_response = ""
                    response_stopped = False
                    stop_response = False  # Reset stop flag
                    
                    try:
                        async for chunk in ai_engine.process_message_stream(
                            user_input, 
                            provider=current_provider, 
                            model=current_model,
                            project_path=current_workspace,
                            conversation_history=conversation_history
                        ):
                            # Check if stop was requested
                            if stop_response:
                                response_stopped = True
                                console.print("\n\n[yellow]⏸️  AI response stopped by user (Ctrl+X)[/yellow]")
                                break
                            
                            # Display character by character for typewriter effect
                            for char in chunk:
                                # Check stop flag during character display too
                                if stop_response:
                                    response_stopped = True
                                    console.print("\n\n[yellow]⏸️  AI response stopped by user (Ctrl+X)[/yellow]")
                                    break
                                console.print(char, end="")
                                full_response += char
                                if typing_delay > 0:
                                    await asyncio.sleep(typing_delay)
                            
                            if response_stopped:
                                break
                    except KeyboardInterrupt:
                        # Ctrl+C pressed - exit chat
                        break
                    
                    console.print()  # New line after streaming
                    console.print("[bold magenta]─[/bold magenta]" * 50)  # Border after AI response
                    
                    # Add AI response to memory (even if stopped)
                    if full_response:
                        memory_manager.add_message("assistant", full_response)
                    
                    # Don't break - continue to next prompt
                    
                except KeyboardInterrupt:
                    # Ctrl+C pressed while waiting for user input - exit chat
                    break
                except Exception as e:
                    console.print(f"ERROR: {str(e)}", style="red")
        
        finally:
            # Save command history
            try:
                readline.write_history_file(str(history_file))
            except Exception:
                pass
            
            server_task.cancel()
            console.print("Chat session ended")
    
    asyncio.run(run_chat())


@main.command()
@click.argument('action')
@click.argument('key', required=False)
@click.argument('value', required=False)
def config(action, key, value):
    """Manage configuration and API keys"""
    config_manager = ConfigManager()
    
    if action == 'list':
        config_data = config_manager.get_config()
        console.print_json(data=config_data)
    elif action == 'set' and key and value:
        config_manager.set_config(key, value)
        console.print(f"SUCCESS: Set {key} = {value}", style="green")
    elif action == 'get' and key:
        value = config_manager.get_config_value(key)
        console.print(f"{key} = {value}")
    elif action == 'delete' and key:
        config_manager.delete_config(key)
        console.print(f"SUCCESS: Deleted {key}", style="green")
    elif action == 'reset':
        config_manager.reset_config()
        console.print("SUCCESS: Configuration reset to defaults", style="green")
    else:
        console.print("ERROR: Invalid config action. Use: list, set <key> <value>, get <key>, delete <key>, reset", style="red")

@main.command()
def providers():
    """List all available AI providers and their endpoints"""
    from .provider_endpoints import PROVIDER_ENDPOINTS, get_all_providers
    
    console.print(Panel.fit("🤖 Available AI Providers & Endpoints", style="bold blue"))
    
    for provider_name in get_all_providers():
        config = PROVIDER_ENDPOINTS[provider_name]
        
        console.print(f"\n[bold cyan]{provider_name.upper()}[/bold cyan]")
        console.print(f"Base URL: [green]{config['base_url']}[/green]")
        
        # List endpoints
        endpoints = {k: v for k, v in config.items() if k.endswith('_endpoint')}
        if endpoints:
            console.print("Endpoints:")
            for endpoint_name, endpoint_path in endpoints.items():
                clean_name = endpoint_name.replace('_endpoint', '').replace('_', ' ').title()
                console.print(f"  • {clean_name}: [yellow]{endpoint_path}[/yellow]")
        
        # Show auth method
        if 'headers' in config:
            auth_header = None
            for key, value in config['headers'].items():
                if 'api_key' in value.lower() or 'authorization' in key.lower():
                    auth_header = f"{key}: {value}"
                    break
            if auth_header:
                console.print(f"Auth: [dim]{auth_header}[/dim]")
        
        if 'auth_param' in config:
            console.print(f"Auth: [dim]URL parameter: {config['auth_param']}[/dim]")

@main.command()
@click.argument('action', required=False)
@click.argument('rule_type', required=False)
@click.argument('args', nargs=-1, required=False)
@click.option('--workspace', '-w', help='Workspace path for workspace rules')
def rules(action, rule_type, args, workspace):
    """Manage global and workspace rules for AI behavior
    
    Examples:
        cognautic rules                                    # List all rules
        cognautic rules add global "Use type hints"       # Add global rule
        cognautic rules add workspace "Follow PEP 8" -w . # Add workspace rule
        cognautic rules remove global 0                   # Remove global rule by index
        cognautic rules clear workspace -w .              # Clear workspace rules
    """
    rules_manager = RulesManager()
    
    if not action:
        # Display all rules
        rules_manager.display_rules(workspace)
        console.print("\nINFO: Usage:")
        console.print("  cognautic rules add global <rule> [description]")
        console.print("  cognautic rules add workspace <rule> [description] -w <path>")
        console.print("  cognautic rules remove global <index>")
        console.print("  cognautic rules remove workspace <index> -w <path>")
        console.print("  cognautic rules clear global")
        console.print("  cognautic rules clear workspace -w <path>")
        return
    
    if action == "add":
        if not rule_type or not args:
            console.print("ERROR: Usage: cognautic rules add <global|workspace> <rule> [description]", style="red")
            return
        
        # Join all args as the rule text
        rule_text = " ".join(args)
        
        if rule_type == "global":
            rules_manager.add_global_rule(rule_text)
        elif rule_type == "workspace":
            if not workspace:
                workspace = os.getcwd()
            rules_manager.add_workspace_rule(rule_text, workspace_path=workspace)
        else:
            console.print("ERROR: Rule type must be 'global' or 'workspace'", style="red")
    
    elif action == "remove":
        if not rule_type or not args:
            console.print("ERROR: Usage: cognautic rules remove <global|workspace> <index>", style="red")
            return
        
        try:
            index = int(args[0])
            if rule_type == "global":
                rules_manager.remove_global_rule(index)
            elif rule_type == "workspace":
                if not workspace:
                    workspace = os.getcwd()
                rules_manager.remove_workspace_rule(index, workspace)
            else:
                console.print("❌ Rule type must be 'global' or 'workspace'", style="red")
        except (ValueError, IndexError):
            console.print("ERROR: Index must be a valid number", style="red")
    
    elif action == "clear":
        if not rule_type:
            console.print("❌ Usage: cognautic rules clear <global|workspace>", style="red")
            return
        
        if rule_type == "global":
            rules_manager.clear_global_rules()
        elif rule_type == "workspace":
            if not workspace:
                workspace = os.getcwd()
            rules_manager.clear_workspace_rules(workspace)
        else:
            console.print("ERROR: Rule type must be 'global' or 'workspace'", style="red")
    
    else:
        console.print(f"❌ Unknown action: {action}", style="red")
        console.print("Valid actions: add, remove, clear")

async def handle_slash_command(command, config_manager, ai_engine, context):
    """Handle slash commands in chat mode"""
    parts = command[1:].split()
    cmd = parts[0].lower() if parts else ""
    
    if cmd == "help":
        show_help()
        return True
    
    elif cmd == "workspace" or cmd == "ws":
        if len(parts) < 2:
            current = context.get('current_workspace')
            if current:
                console.print(f"DIR: Current workspace: {current}")
            else:
                console.print("DIR: No workspace set")
            console.print("Usage: /workspace <path> or /ws <path>")
        else:
            path_input = parts[1]
            
            # First expand user home directory
            new_path = Path(path_input).expanduser()
            
            # Then handle relative vs absolute paths
            if not new_path.is_absolute():
                # Relative path from original working directory
                original_cwd = context.get('original_cwd', os.getcwd())
                new_path = Path(original_cwd) / new_path
            
            # Resolve to absolute path
            new_path = new_path.resolve()
            
            if new_path.exists() and new_path.is_dir():
                context['current_workspace'] = str(new_path)
                console.print(f"SUCCESS: Workspace changed to: {new_path}")
                console.print(f"INFO: AI will now create files in this directory")
            else:
                console.print(f"ERROR: Directory not found: {new_path}", style="red")
        return True
    
    elif cmd == "setup":
        console.print("🔧 Running setup wizard...")
        config_manager.interactive_setup()
        return True
    
    elif cmd == "config":
        if len(parts) < 2:
            console.print("Available config commands:")
            console.print("• /config list - Show current configuration")
            console.print("• /config providers - Show available providers")
            console.print("• /config set <key> <value> - Set configuration value")
        elif parts[1] == "list":
            config_data = config_manager.get_config()
            console.print_json(data=config_data)
        elif parts[1] == "providers":
            providers = config_manager.list_providers()
            console.print(f"Available providers: {', '.join(providers) if providers else 'None'}")
        elif parts[1] == "set" and len(parts) >= 4:
            config_manager.set_config(parts[2], parts[3])
            console.print(f"SUCCESS: Set {parts[2]} = {parts[3]}")
        return True
    
    elif cmd == "provider":
        if len(parts) < 2:
            current_provider = context.get('provider')
            console.print(f"Current provider: {current_provider}")
            providers = config_manager.list_providers()
            # Add local provider if available
            if 'local' in ai_engine.providers:
                providers.append('local')
            console.print(f"Available providers: {', '.join(providers)}")
            console.print("Usage: /provider <provider_name>")
        else:
            new_provider = parts[1]
            # Check if it's the local provider or has an API key
            if new_provider == 'local':
                # Check if local model is configured
                local_model_path = config_manager.get_config_value('local_model_path')
                if local_model_path:
                    # Load the local model if not already loaded
                    if 'local' not in ai_engine.providers:
                        try:
                            console.print(f"INFO: Loading local model from: {local_model_path}")
                            ai_engine.load_local_model(local_model_path)
                            console.print("SUCCESS: Local model loaded successfully!")
                        except Exception as e:
                            console.print(f"ERROR: Error loading local model: {e}", style="red")
                            return True
                    
                    context['provider'] = new_provider
                    current_provider = new_provider  # Update current provider
                    # Save the provider choice
                    config_manager.set_config('last_provider', new_provider)
                    # Load saved model for this provider
                    saved_model = config_manager.get_provider_model(new_provider)
                    context['model'] = saved_model
                    current_model = saved_model  # Update current model
                    console.print(f"SUCCESS: Switched to provider: {new_provider}")
                    if saved_model:
                        console.print(f"INFO: Using saved model: {saved_model}")
                else:
                    console.print("ERROR: No local model configured", style="red")
                    console.print("INFO: Use /lmodel <path> to load a local model first", style="yellow")
            elif config_manager.has_api_key(new_provider):
                context['provider'] = new_provider
                current_provider = new_provider  # Update current provider
                # Save the provider choice
                config_manager.set_config('last_provider', new_provider)
                # Load saved model for this provider
                saved_model = config_manager.get_provider_model(new_provider)
                context['model'] = saved_model
                current_model = saved_model  # Update current model
                console.print(f"SUCCESS: Switched to provider: {new_provider}")
                if saved_model:
                    console.print(f"INFO: Using saved model: {saved_model}")
            else:
                console.print(f"ERROR: Provider {new_provider} not configured", style="red")
                if new_provider == 'local':
                    console.print("INFO: Use /lmodel <path> to load a local model first", style="yellow")
        return True
    
    elif cmd == "model" or cmd == "models":
        current_provider = context.get('provider')
        if not current_provider:
            console.print("ERROR: No provider selected", style="red")
            return True
        
        # Check if user wants to list models (fetch from API)
        if len(parts) >= 2 and parts[1] == "list":
            console.print(f"INFO: Fetching available models from {current_provider}...")
            
            try:
                # Import API client
                from .provider_endpoints import GenericAPIClient, get_provider_config
                
                # Get API key
                config_manager = context.get('config_manager')
                api_key = config_manager.get_api_key(current_provider)
                
                if not api_key:
                    console.print(f"ERROR: No API key configured for {current_provider}", style="red")
                    console.print(f"INFO: Run /setup to configure your API key")
                    return True
                
                # Create API client and fetch models
                client = GenericAPIClient(current_provider, api_key)
                
                # Check if provider has models endpoint
                provider_config = get_provider_config(current_provider)
                if 'models_endpoint' not in provider_config:
                    console.print(f"INFO: {current_provider} doesn't provide a models API endpoint")
                    console.print(f"INFO: Check the provider's documentation for available models:")
                    
                    # Show documentation links
                    docs = {
                        'openai': 'https://platform.openai.com/docs/models',
                        'anthropic': 'https://docs.anthropic.com/claude/docs/models-overview',
                        'google': 'https://ai.google.dev/gemini-api/docs/models/gemini',
                        'together': 'https://docs.together.ai/docs/inference-models',
                        'openrouter': 'https://openrouter.ai/models',
                        'groq': 'https://console.groq.com/docs/models',
                        'mistral': 'https://docs.mistral.ai/getting-started/models/',
                        'deepseek': 'https://platform.deepseek.com/api-docs/',
                        'perplexity': 'https://docs.perplexity.ai/docs/model-cards',
                        'cohere': 'https://docs.cohere.com/docs/models',
                    }
                    
                    if current_provider in docs:
                        console.print(f"   {docs[current_provider]}")
                    
                    return True
                
                # Fetch models from API
                import asyncio
                import nest_asyncio
                
                # Allow nested event loops
                try:
                    nest_asyncio.apply()
                except:
                    pass
                
                # Try to get models
                try:
                    result = asyncio.run(client.list_models())
                except RuntimeError:
                    # If we're in an event loop, use a workaround
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, client.list_models())
                        result = future.result(timeout=10)
                
                if 'data' in result:
                    models = result['data']
                    console.print(f"\n[bold cyan]Available models for {current_provider}:[/bold cyan]")
                    for i, model in enumerate(models[:20], 1):  # Show first 20
                        model_id = model.get('id') or model.get('name') or str(model)
                        console.print(f"  {i}. {model_id}")
                    
                    if len(models) > 20:
                        console.print(f"\n... and {len(models) - 20} more models")
                    
                    console.print(f"\nINFO: Use: /model <model_name> to switch")
                elif 'models' in result:
                    models = result['models']
                    console.print(f"\n[bold cyan]Available models for {current_provider}:[/bold cyan]")
                    for i, model in enumerate(models[:20], 1):
                        model_name = model.get('name', '').replace('models/', '')
                        console.print(f"  {i}. {model_name}")
                    
                    if len(models) > 20:
                        console.print(f"\n... and {len(models) - 20} more models")
                    
                    console.print(f"\nINFO: Use: /model <model_name> to switch")
                else:
                    console.print(f"WARNING: Unexpected response format from {current_provider}")
                    console.print(f"INFO: Check the provider's documentation for available models")
                    
            except Exception as e:
                console.print(f"ERROR: Error fetching models: {str(e)}", style="red")
                console.print(f"INFO: Check the provider's documentation for available models")
        
        elif len(parts) < 2:
            # Show current model and hint
            current_model = context.get('model')
            console.print(f"📌 Current model: {current_model or 'default'}")
            console.print(f"📌 Provider: {current_provider}")
            console.print(f"\nINFO: Use: /model list - to fetch available models from API")
            console.print(f"INFO: Use: /model <model_name> - to switch model")
        else:
            # Switch to new model
            new_model = parts[1]
            context['model'] = new_model
            
            # Save the model preference for the current provider and globally
            current_provider = context.get('provider')
            config_manager = context.get('config_manager')
            if config_manager:
                # Save as last used model globally
                config_manager.set_config('last_model', new_model)
                # Save as default for this provider
                if current_provider:
                    config_manager.set_provider_model(current_provider, new_model)
                    console.print(f"SUCCESS: Switched to model: {new_model}")
                    console.print(f"INFO: Model saved as default for provider: {current_provider}")
                else:
                    console.print(f"SUCCESS: Switched to model: {new_model}")
            else:
                console.print(f"SUCCESS: Switched to model: {new_model}")
        return True
    
    elif cmd == "session":
        memory_manager = context.get('memory_manager')
        if not memory_manager:
            console.print("ERROR: Memory manager not available", style="red")
            return True
        
        if len(parts) < 2:
            # Show current session info and list available sessions
            current_session = memory_manager.get_current_session()
            if current_session:
                console.print(f"SESSION: Current session: {current_session.session_id} - {current_session.title}")
                console.print(f"   Created: {current_session.created_at}")
                console.print(f"   Messages: {current_session.message_count}")
                console.print(f"   Provider: {current_session.provider}")
                if current_session.model:
                    console.print(f"   Model: {current_session.model}")
            else:
                console.print("SESSION: No active session")
            
            console.print("\nAvailable commands:")
            console.print("• /session list - List all sessions")
            console.print("• /session new - Create new session")
            console.print("• /session load <id> - Load existing session")
            console.print("• /session delete <id> - Delete session")
            console.print("• /session export <id> [format] - Export session")
            console.print("• /session title <new_title> - Update session title")
        
        elif parts[1] == "list":
            sessions = memory_manager.list_sessions()
            if not sessions:
                console.print("SESSION: No sessions found")
            else:
                console.print(f"SESSION: Found {len(sessions)} sessions:")
                for idx, session in enumerate(sessions[:10], 1):  # Show last 10 sessions with index
                    console.print(f"   [{idx}] {session.session_id} - {session.title}")
                    console.print(f"      {session.message_count} messages, {session.provider}")
                    console.print(f"      Last updated: {session.last_updated}")
                    console.print()
        
        elif parts[1] == "new":
            # Create new session (will replace current one)
            current_provider = context.get('provider', 'openai')
            current_model = context.get('model')
            current_workspace = context.get('current_workspace')
            
            session_id = memory_manager.create_session(
                provider=current_provider,
                model=current_model,
                workspace=current_workspace
            )
        
        elif parts[1] == "load" and len(parts) >= 3:
            session_identifier = parts[2]
            
            # Check if it's a numeric index
            if session_identifier.isdigit():
                index = int(session_identifier)
                sessions = memory_manager.list_sessions()
                if 1 <= index <= len(sessions):
                    session_id = sessions[index - 1].session_id
                else:
                    console.print(f"[red]Invalid session index: {index}. Use /session list to see available sessions.[/red]")
                    return True
            else:
                session_id = session_identifier
            
            if memory_manager.load_session(session_id):
                # Update context with session info
                current_session = memory_manager.get_current_session()
                context['provider'] = current_session.provider
                context['model'] = current_session.model
                context['current_workspace'] = current_session.workspace
        
        elif parts[1] == "delete" and len(parts) >= 3:
            session_id = parts[2]
            memory_manager.delete_session(session_id)
        
        elif parts[1] == "export" and len(parts) >= 3:
            session_id = parts[2]
            format_type = parts[3] if len(parts) >= 4 else "json"
            memory_manager.export_session(session_id, format_type)
        
        elif parts[1] == "title" and len(parts) >= 3:
            new_title = " ".join(parts[2:])
            memory_manager.update_session_info(title=new_title)
            console.print(f"SUCCESS: Updated session title to: {new_title}")
        
        else:
            console.print("ERROR: Invalid session command. Use /session for help.", style="red")
        
        return True
    
    elif cmd == "lmodel":
        if len(parts) < 2:
            # Show current local model status
            local_model_path = config_manager.get_config_value('local_model_path')
            if local_model_path:
                console.print(f"MODEL: Current local model: {local_model_path}")
                console.print("INFO: Use: /lmodel <path> - to load a different model")
                console.print("INFO: Use: /lmodel unload - to unload the current model")
                console.print("INFO: Use: /provider local - to switch to local model")
            else:
                console.print("MODEL: No local model loaded")
                console.print("\nUsage: /lmodel <model_path>")
                console.print("\nExamples:")
                console.print("  /lmodel ~/models/llama-2-7b")
                console.print("  /lmodel /path/to/huggingface/model")
                console.print("  /lmodel microsoft/phi-2")
                console.print("\nINFO: You can use:")
                console.print("  • Local path to a downloaded model")
                console.print("  • Hugging Face model ID (will download if needed)")
        elif parts[1] == "unload":
            # Unload the local model
            try:
                ai_engine.unload_local_model()
                console.print("SUCCESS: Local model unloaded successfully")
                # If current provider is local, switch to default
                if context.get('provider') == 'local':
                    available_providers = config_manager.list_providers()
                    if available_providers:
                        context['provider'] = available_providers[0]
                        console.print(f"SUCCESS: Switched to provider: {available_providers[0]}")
            except Exception as e:
                console.print(f"ERROR: Error unloading model: {e}", style="red")
        else:
            # Load a new local model
            model_path = " ".join(parts[1:])
            console.print(f"INFO: Loading local model from: {model_path}")
            console.print("⏳ This may take a few minutes depending on model size...")
            
            try:
                ai_engine.load_local_model(model_path)
                console.print("SUCCESS: Local model loaded successfully!")
                console.print("INFO: Use: /provider local - to switch to the local model")
                console.print("INFO: Or the model will be used automatically if 'local' is your default provider")
            except Exception as e:
                console.print(f"ERROR: Error loading model: {e}", style="red")
                console.print("\nINFO: Make sure you have installed the required dependencies:")
                console.print("   pip install transformers torch accelerate")
        return True
    
    elif cmd == "speed":
        config_manager = context.get('config_manager') or config_manager
        
        if len(parts) < 2:
            # Show current speed
            current_speed = config_manager.get_config_value('typing_speed') or 'fast'
            console.print(f"⚡ Current typing speed: {current_speed}")
            console.print("\nAvailable speeds:")
            console.print("  • instant - No delay (immediate)")
            console.print("  • fast    - 0.001s per character (~1000 chars/sec) [default]")
            console.print("  • normal  - 0.005s per character (~200 chars/sec)")
            console.print("  • slow    - 0.01s per character (~100 chars/sec)")
            console.print("  • <number> - Custom delay in seconds")
            console.print("\nUsage: /speed <instant|fast|normal|slow|number>")
        else:
            new_speed = parts[1]
            
            # Validate speed
            valid_speeds = ['instant', 'fast', 'normal', 'slow']
            try:
                # Try to parse as number
                float(new_speed)
                is_valid = True
            except ValueError:
                is_valid = new_speed in valid_speeds
            
            if is_valid:
                config_manager.set_config('typing_speed', new_speed)
                console.print(f"SUCCESS: Typing speed set to: {new_speed}")
            else:
                console.print(f"ERROR: Invalid speed: {new_speed}", style="red")
                console.print("Valid options: instant, fast, normal, slow, or a number")
        
        return True
    
    elif cmd == "rules" or cmd == "rule":
        rules_manager = RulesManager()
        current_workspace = context.get('current_workspace')
        
        if len(parts) < 2:
            # Display all rules
            rules_manager.display_rules(current_workspace)
            console.print("\n💡 Commands:")
            console.print("  /rules add global <rule> [description]")
            console.print("  /rules add workspace <rule> [description]")
            console.print("  /rules remove global <index>")
            console.print("  /rules remove workspace <index>")
            console.print("  /rules clear global")
            console.print("  /rules clear workspace")
        
        elif parts[1] == "add":
            if len(parts) < 4:
                console.print("❌ Usage: /rules add <global|workspace> <rule> [description]", style="red")
            else:
                rule_type = parts[2].lower()
                # Find where description starts (after the rule text)
                rule_parts = []
                description_parts = []
                in_description = False
                
                for i, part in enumerate(parts[3:], 3):
                    if part.startswith('[') and not in_description:
                        in_description = True
                        description_parts.append(part[1:])
                    elif in_description:
                        if part.endswith(']'):
                            description_parts.append(part[:-1])
                            break
                        else:
                            description_parts.append(part)
                    else:
                        rule_parts.append(part)
                
                rule = " ".join(rule_parts)
                description = " ".join(description_parts) if description_parts else ""
                
                if rule_type == "global":
                    rules_manager.add_global_rule(rule, description)
                elif rule_type == "workspace":
                    rules_manager.add_workspace_rule(rule, description, current_workspace)
                else:
                    console.print("❌ Rule type must be 'global' or 'workspace'", style="red")
        
        elif parts[1] == "remove":
            if len(parts) < 4:
                console.print("ERROR: Usage: /rules remove <global|workspace> <index>", style="red")
            else:
                rule_type = parts[2].lower()
                try:
                    index = int(parts[3])
                    if rule_type == "global":
                        rules_manager.remove_global_rule(index)
                    elif rule_type == "workspace":
                        rules_manager.remove_workspace_rule(index, current_workspace)
                    else:
                        console.print("ERROR: Rule type must be 'global' or 'workspace'", style="red")
                except ValueError:
                    console.print("ERROR: Index must be a number", style="red")
        
        elif parts[1] == "clear":
            if len(parts) < 3:
                console.print("ERROR: Usage: /rules clear <global|workspace>", style="red")
            else:
                rule_type = parts[2].lower()
                if rule_type == "global":
                    rules_manager.clear_global_rules()
                elif rule_type == "workspace":
                    rules_manager.clear_workspace_rules(current_workspace)
                else:
                    console.print("ERROR: Rule type must be 'global' or 'workspace'", style="red")
        
        else:
            console.print("ERROR: Invalid rules command. Use /rules for help.", style="red")
        
        return True
    
    elif cmd == "clear":
        console.clear()
        console.print("Chat cleared")
        return True
    
    elif cmd == "ps" or cmd == "processes":
        # List all running background processes
        try:
            result = await ai_engine.tool_registry.execute_tool(
                "command_runner",
                operation="check_process_status",
                user_id="ai_engine"
            )
            
            if result.success and result.data:
                processes = result.data.get('processes', [])
                if not processes:
                    console.print("PROCESS: No background processes running", style="dim")
                else:
                    console.print(f"\nPROCESS: Running Processes ({len(processes)}):", style="bold")
                    for proc in processes:
                        status_color = "green" if proc['status'] == 'running' else "yellow"
                        console.print(f"  • PID: {proc['process_id']} - {proc['command'][:50]}... [{proc['status']}]", style=status_color)
                        console.print(f"    Running for: {proc['running_time']:.1f}s", style="dim")
                    console.print("\nINFO: Use /ct <process_id> to terminate a process\n", style="dim")
            else:
                console.print("ERROR: Failed to get process list", style="red")
        except Exception as e:
            console.print(f"ERROR: {str(e)}", style="red")
        
        return True
    
    elif cmd == "ct" or cmd == "cancel":
        # Cancel/terminate a background process
        if len(parts) < 2:
            console.print("ERROR: Usage: /ct <process_id>", style="red")
            console.print("INFO: Tip: Process IDs are shown when commands run in background", style="dim")
            return True
        
        process_id = parts[1]
        try:
            result = await ai_engine.tool_registry.execute_tool(
                "command_runner",
                operation="kill_process",
                process_id=process_id,
                user_id="ai_engine"
            )
            
            if result.success:
                console.print(f"SUCCESS: Process {process_id} terminated successfully", style="green")
            else:
                console.print(f"ERROR: Failed to terminate process: {result.error}", style="red")
        except Exception as e:
            console.print(f"ERROR: {str(e)}", style="red")
        
        return True
    
    elif cmd == "exit" or cmd == "quit":
        return False
    
    else:
        console.print(f"ERROR: Unknown command: /{cmd}. Type /help for available commands.", style="red")
        return True

def show_help():
    """Show help information"""
    help_text = Text()
    help_text.append("Available commands:\n", style="bold")
    help_text.append("• Press Shift+Tab - Toggle between Chat and Terminal modes\n", style="bold yellow")
    help_text.append("• /help - Show this help message\n")
    help_text.append("• /workspace <path> or /ws <path> - Change working directory\n")
    help_text.append("• /setup - Run interactive setup wizard\n")
    help_text.append("• /config [list|providers|set <key> <value>] - Manage configuration\n")
    help_text.append("• /provider [name] - Switch AI provider\n")
    help_text.append("• /model [model_id] - Switch AI model\n")
    help_text.append("• /model list or /models - Fetch available models from provider's API\n")
    help_text.append("• /lmodel <model_path> - Load local Hugging Face model\n")
    help_text.append("• /lmodel unload - Unload current local model\n")
    help_text.append("• /session [list|new|load <id>|delete <id>|export <id>] - Manage chat sessions\n")
    help_text.append("• /rules - Manage global and workspace rules for AI behavior\n")
    help_text.append("  - /rules add global <rule> [description] - Add a global rule\n", style="dim")
    help_text.append("  - /rules add workspace <rule> [description] - Add a workspace rule\n", style="dim")
    help_text.append("  - /rules remove global <index> - Remove a global rule\n", style="dim")
    help_text.append("  - /rules remove workspace <index> - Remove a workspace rule\n", style="dim")
    help_text.append("  - /rules clear global|workspace - Clear all rules of a type\n", style="dim")
    help_text.append("• /speed [instant|fast|normal|slow|<number>] - Set typing speed for AI responses\n")
    help_text.append("• /ps or /processes - List all running background processes\n")
    help_text.append("• /ct <process_id> or /cancel <process_id> - Terminate a background process\n")
    help_text.append("• /clear - Clear chat screen\n")
    help_text.append("• /exit or /quit - Exit chat session\n")
    help_text.append("• exit or quit - Exit chat session\n")
    help_text.append("\n")
    help_text.append("CLI Commands (use outside chat):\n", style="bold cyan")
    help_text.append("• cognautic providers - List all AI providers and their API endpoints\n", style="cyan")
    help_text.append("\n• Any other text will be sent to the AI\n")
    
    console.print(Panel(help_text, title="Cognautic CLI Help", style="blue"))

if __name__ == '__main__':
    main()
