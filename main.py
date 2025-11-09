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


def parse_custom_datetime(datetime_str):
    """Parse datetime string in mmddyy hhmm format"""
    if datetime_str:
        try:
            return datetime.strptime(datetime_str, "%m%d%y %H%M")
        except ValueError:
            print(f"❌ Invalid datetime format: {datetime_str}. Please use 'mmddyy HHMM'.")
            exit(1)
    return None


def get_agent_class(agent_type):
    """
    Dynamically import and return the corresponding class based on agent type name
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
        import importlib

        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        print(f"✅ Successfully loaded Agent class: {agent_type} (from {module_path})")
        return agent_class
    except ImportError as e:
        raise ImportError(f"❌ Unable to import agent module {module_path}: {e}")
    except AttributeError as e:
        raise AttributeError(f"❌ Class {class_name} not found in module {module_path}: {e}")


def load_config(config_path=None):
    """
    Load configuration file from configs directory
    """
    if config_path is None:
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


async def main(config_path=None):  # noqa: C901
    """Run trading experiment using BaseAgent class"""
    config = load_config(config_path)
    agent_type = config.get("agent_type", "BaseAgent")
    try:
        AgentClass = get_agent_class(agent_type)
    except (ValueError, ImportError, AttributeError) as e:
        print(str(e))
        exit(1)

    start_datetime_str = os.getenv("START_DATETIME")
    end_datetime_str = os.getenv("END_DATETIME")

    start_datetime = parse_custom_datetime(start_datetime_str)
    end_datetime = parse_custom_datetime(end_datetime_str)

    if start_datetime and end_datetime:
        INIT_DATE = start_datetime.strftime("%Y-%m-%d")
        END_DATE = end_datetime.strftime("%Y-%m-%d")
        start_time = start_datetime.strftime("%H:%M")
        end_time = end_datetime.strftime("%H:%M")
        print("⚠️  Using START_DATETIME and END_DATETIME environment variables.")
        print(f"   INIT_DATE: {INIT_DATE}, END_DATE: {END_DATE}")
        print(f"   start_time: {start_time}, end_time: {end_time}")
    else:
        today_dt = datetime.now()
        yesterday_dt = today_dt - timedelta(days=1)
        start_datetime = yesterday_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        # If end_datetime_str was empty, default end_datetime to current time
        if not end_datetime_str:
            end_datetime = today_dt # Use current time
        else:
            end_datetime = today_dt.replace(hour=9, minute=30, second=0, microsecond=0) # Keep original default if end_datetime_str was not empty but invalid
        INIT_DATE = start_datetime.strftime("%Y-%m-%d")
        END_DATE = end_datetime.strftime("%Y-%m-%d")
        start_time = start_datetime.strftime("%H:%M")
        end_time = end_datetime.strftime("%H:%M")
        print("⚠️  No datetime provided. Using default: yesterday 9:30 to today current time.")

    INIT_DATE_obj = datetime.strptime(INIT_DATE, "%Y-%m-%d").date()
    END_DATE_obj = datetime.strptime(END_DATE, "%Y-%m-%d").date()
    if INIT_DATE_obj > END_DATE_obj:
        print("❌ INIT_DATE is greater than END_DATE")
        exit(1)

    enabled_models = [model for model in config["models"] if model.get("enabled", True)]

    for model in enabled_models:
        if model.get("openai_api_key") == "{{DEEPSEEK_API_KEY}}":
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                print("❌ DEEPSEEK_API_KEY environment variable not set.")
                exit(1)
            model["openai_api_key"] = deepseek_api_key

    agent_config = config.get("agent_config", {})
    log_config = config.get("log_config", {})
    max_steps = agent_config.get("max_steps", 10)
    max_retries = agent_config.get("max_retries", 3)
    base_delay = agent_config.get("base_delay", 0.5)
    initial_cash = agent_config.get("initial_cash", 10000.0)

    for model_config in enabled_models:
        model_name = model_config.get("name", "unknown")
        basemodel = model_config.get("basemodel")
        signature = model_config.get("signature")
        openai_base_url = model_config.get("openai_base_url", None)
        openai_api_key = model_config.get("openai_api_key", None)

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

        os.environ["SIGNATURE"] = signature
        os.environ["TODAY_DATE"] = END_DATE
        os.environ["IF_TRADE"] = "False"

        log_path = log_config.get("log_path", "./data/agent_data")

        asset_type = os.getenv("ASSET_TYPE", "stock").lower()
        if config.get("crypto_mode"):
            asset_type = "crypto"
        elif config.get("futures_mode"):
            asset_type = "futures"

        trading_symbols_env = os.getenv("TRADING_SYMBOLS", "").strip()
        if trading_symbols_env:
            trading_symbols = [s.strip().upper() for s in trading_symbols_env.split(",")]
            print(f"📊 Trading symbols (from workflow input): {trading_symbols}")
            print(f"💱 Asset type (from workflow input): {asset_type}")
        elif config.get("trading_universe"):
            trading_symbols = config.get("trading_universe")
            print(f"📊 Trading symbols (from config): {trading_symbols}")
        else:
            trading_symbols = all_nasdaq_100_symbols
            print(f"📊 Trading symbols: {len(trading_symbols)} NASDAQ 100 stocks (default)")

        try:
            trade_style = os.getenv("TRADE_STYLE", "swing").lower()
            print(f"💱 Trading style: {trade_style}")

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

            await agent.initialize()
            print("✅ Initialization successful")
            print("🔄 About to call run_date_range...")
            try:
                print(f"📝 start_time={start_time}, end_time={end_time}, INIT_DATE={INIT_DATE}, END_DATE={END_DATE}")
                await agent.run_date_range(INIT_DATE, END_DATE)
            except NameError as ne:
                print(f"🔥 NameError caught in run_date_range: {ne}")
                import traceback
                traceback.print_exc()
                raise

            summary = agent.get_position_summary()
            print("📊 Final position summary:")
            print(f"   - Latest date: {summary.get('latest_date')}")
            print(f"   - Total records: {summary.get('total_records')}")
            print(f"   - Cash balance: ${summary.get('positions', {}).get('CASH', 0):.2f}")

        except Exception as e:
            print(f"❌ Error processing model {model_name} ({signature}): {str(e)}")
            print(f"📋 Error details: {e}")
            import sys
            import traceback
            print("\n📋 Full traceback:")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            exit(1)

        print("=" * 60)
        print(f"✅ Model {model_name} ({signature}) processing completed")
        print("=" * 60)

    print("🎉 All models processing completed!")


if __name__ == "__main__":
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    if config_path:
        print(f"📄 Using specified configuration file: {config_path}")
    else:
        print("📄 Using default configuration file: configs/default_config.json")

    asyncio.run(main(config_path))