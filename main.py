import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from prompts.agent_prompt import all_nasdaq_100_symbols
from tools.general_tools import get_config_value, write_config_value

load_dotenv()

# Agent class mapping table - for dynamic import and instantiation
AGENT_REGISTRY = {
    "BaseAgent": {"module": "agent.base_agent.base_agent", "class": "BaseAgent"},
}


def get_agent_class(agent_type):
    """
    Dynamically import and return the corresponding class based on agent type name

    Args:
        agent_type: Agent type name (e.g., "BaseAgent")

    Returns:
        Agent class

    Raises:
        ValueError: If agent type is not supported
        ImportError: If unable to import agent module
    """
    if agent_type not in AGENT_REGISTRY:
        supported_types = ", ".join(AGENT_REGISTRY.keys())
        raise ValueError(
            f"❌ Unsupported agent type: {agent_type}\n"
            f"   Supported types: {supported_types}"
        )

    agent_info = AGENT_REGISTRY[agent_type]
    module_path = agent_info["module"]
    class_name = agent_info["class"]

    try:
        # Dynamic import module
        import importlib

        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        print(f"✅ Successfully loaded Agent class: {agent_type} (from {module_path})")
        return agent_class
    except ImportError as e:
        raise ImportError(f"❌ Unable to import agent module {module_path}: {e}")
    except AttributeError as e:
        raise AttributeError(
            f"❌ Class {class_name} not found in module {module_path}: {e}"
        )


def load_config(config_path=None):
    """
    Load configuration file from configs directory

    Args:
        config_path: Configuration file path, if None use default config

    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        # Default configuration file path
        config_path = Path(__file__).parent / "configs" / "default_config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        print(f"❌ Configuration file does not exist: {config_path}")
        exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"✅ Successfully loaded configuration file: {config_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Configuration file JSON format error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Failed to load configuration file: {e}")
        exit(1)


async def main(config_path=None):
    """Run trading experiment using BaseAgent class

    Args:
        config_path: Configuration file path, if None use default config
    """
    # Load configuration file
    config = load_config(config_path)

    # Get Agent type
    agent_type = config.get("agent_type", "BaseAgent")
    try:
        AgentClass = get_agent_class(agent_type)
    except (ValueError, ImportError, AttributeError) as e:
        print(str(e))
        exit(1)

    # Get date range from configuration file
    INIT_DATE = config["date_range"]["init_date"]
    END_DATE = config["date_range"]["end_date"]

    # Environment variables can override dates in configuration file
    if os.getenv("INIT_DATE"):
        INIT_DATE = os.getenv("INIT_DATE")
        print(f"⚠️  Using environment variable to override INIT_DATE: {INIT_DATE}")
    if os.getenv("END_DATE"):
        END_DATE = os.getenv("END_DATE")
        print(f"⚠️  Using environment variable to override END_DATE: {END_DATE}")

    # Dynamic date handling
    def parse_dynamic_date(date_str):
        """Parse dynamic date strings like TODAY, TODAY-1, TODAY-7"""
        if date_str.startswith("TODAY"):
            days_offset = 0
            if "-" in date_str and date_str != "TODAY":
                try:
                    days_offset = -int(date_str.split("-", 1)[1])
                except (ValueError, IndexError):
                    pass
            return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        return date_str

    INIT_DATE = parse_dynamic_date(INIT_DATE)
    END_DATE = parse_dynamic_date(END_DATE)

    # Validate date range
    INIT_DATE_obj = datetime.strptime(INIT_DATE, "%Y-%m-%d").date()
    END_DATE_obj = datetime.strptime(END_DATE, "%Y-%m-%d").date()
    if INIT_DATE_obj > END_DATE_obj:
        print("❌ INIT_DATE is greater than END_DATE")
        exit(1)

    # Get trading session times
    trading_session_config = config.get("trading_session", {})
    start_time = os.getenv("START_TIME", trading_session_config.get("start_time", "09:30"))
    end_time = os.getenv("END_TIME", trading_session_config.get("end_time", "16:00"))

    if os.getenv("START_TIME"):
        print(f"⚠️  Using environment variable to override start_time: {start_time}")
    if os.getenv("END_TIME"):
        print(f"⚠️  Using environment variable to override end_time: {end_time}")

    # Get model list from configuration file (only select enabled models)
    enabled_models = [model for model in config["models"] if model.get("enabled", True)]

    # Replace API key placeholders
    for model in enabled_models:
        if model.get("openai_api_key") == "{{DEEPSEEK_API_KEY}}":
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                print("❌ DEEPSEEK_API_KEY environment variable not set.")
                exit(1)
            model["openai_api_key"] = deepseek_api_key

    # Get agent configuration
    agent_config = config.get("agent_config", {})
    log_config = config.get("log_config", {})
    max_steps = agent_config.get("max_steps", 10)
    max_retries = agent_config.get("max_retries", 3)
    base_delay = agent_config.get("base_delay", 0.5)
    initial_cash = agent_config.get("initial_cash", 10000.0)

    # Display enabled model information
    model_names = [m.get("name", m.get("signature")) for m in enabled_models]


    for model_config in enabled_models:
        # Read basemodel and signature directly from configuration file
        model_name = model_config.get("name", "unknown")
        basemodel = model_config.get("basemodel")
        signature = model_config.get("signature")
        openai_base_url = model_config.get("openai_base_url", None)
        openai_api_key = model_config.get("openai_api_key", None)

        # Validate required fields
        if not basemodel:
            print(f"❌ Model {model_name} missing basemodel field")
            continue
        if not signature:
            print(f"❌ Model {model_name} missing signature field")
            continue

        print("=" * 60)
        print(f"🤖 Processing model: {model_name}")
        print(f"📝 Signature: {signature}")
        print(f"🔧 BaseModel: {basemodel}")

        # Initialize runtime configuration
        os.environ["SIGNATURE"] = signature
        os.environ["TODAY_DATE"] = END_DATE
        os.environ["IF_TRADE"] = "False"

        # Get log path configuration
        log_path = log_config.get("log_path", "./data/agent_data")

        # Determine trading symbols based on priority:
        # 1. Environment variables (from workflow inputs) - highest priority
        # 2. Config file (trading_universe) - medium priority
        # 3. Default NASDAQ 100 stocks - lowest priority

        asset_type = os.getenv("ASSET_TYPE", "stock").lower()
        if config.get("crypto_mode"):
            asset_type = "crypto"
        elif config.get("futures_mode"):
            asset_type = "futures"

        trading_symbols_env = os.getenv("TRADING_SYMBOLS", "").strip()

        if trading_symbols_env:
            # Environment variable takes precedence - user specified symbols via workflow input
            trading_symbols = [s.strip().upper() for s in trading_symbols_env.split(",")]
            print(f"📊 Trading symbols (from workflow input): {trading_symbols}")
            print(f"💱 Asset type (from workflow input): {asset_type}")
        elif config.get("trading_universe"):
            # Config file specifies trading universe
            trading_symbols = config.get("trading_universe")
            print(f"📊 Trading symbols (from config): {trading_symbols}")
        else:
            # Default to NASDAQ 100 stocks
            trading_symbols = all_nasdaq_100_symbols
            print(f"📊 Trading symbols: {len(trading_symbols)} NASDAQ 100 stocks (default)")

        try:
            # Get trading style from environment or config (default: swing)
            trade_style = os.getenv("TRADE_STYLE", "swing").lower()
            print(f"💱 Trading style: {trade_style}")

            # Dynamically create Agent instance
            agent = AgentClass(
                signature=signature,
                basemodel=basemodel,
                asset_type=asset_type,
                stock_symbols=trading_symbols,
                log_path=log_path,
                openai_base_url=openai_base_url,
                openai_api_key=openai_api_key,
                max_steps=max_steps,
                max_retries=max_retries,
                base_delay=base_delay,
                initial_cash=initial_cash,
                init_date=INIT_DATE,
                trade_style=trade_style,
                start_time=start_time,
                end_time=end_time,
            )

            print(f"✅ {agent_type} instance created successfully: {agent}")

            # Initialize MCP connection and AI model
            await agent.initialize()
            print("✅ Initialization successful")
            # Run all trading days in date range
            print(f"Calling run_date_range with start_time={start_time} and end_time={end_time}")
            await agent.run_date_range(INIT_DATE, END_DATE)

            # Display final position summary
            summary = agent.get_position_summary()
            print(f"📊 Final position summary:")
            print(f"   - Latest date: {summary.get('latest_date')}")
            print(f"   - Total records: {summary.get('total_records')}")
            print(
                f"   - Cash balance: ${summary.get('positions', {}).get('CASH', 0):.2f}"
            )

        except Exception as e:
            print(f"❌ Error processing model {model_name} ({signature}): {str(e)}")
            print(f"📋 Error details: {e}")
            # Print full traceback for debugging
            import traceback
            import sys
            print("\n📋 Full traceback:")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            # Can choose to continue processing next model, or exit
            # continue  # Continue processing next model
            exit(1)  # Or exit program

        print("=" * 60)
        print(f"✅ Model {model_name} ({signature}) processing completed")
        print("=" * 60)

    print("🎉 All models processing completed!")


if __name__ == "__main__":
    import sys

    # Support specifying configuration file through command line arguments
    # Usage: python livebaseagent_config.py [config_path]
    # Example: python livebaseagent_config.py configs/my_config.json
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    if config_path:
        print(f"📄 Using specified configuration file: {config_path}")
    else:
        print(f"📄 Using default configuration file: configs/default_config.json")

    asyncio.run(main(config_path))
