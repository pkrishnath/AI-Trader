"""
BaseAgent class - Base class for trading agents
Encapsulates core functionality including MCP tool management, AI agent creation, and trading execution
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from prompts.agent_prompt import STOP_SIGNAL, get_agent_system_prompt
from prompts.crypto_agent_prompt import get_crypto_agent_system_prompt
from prompts.futures_agent_prompt import get_futures_agent_system_prompt
from tools.enhanced_logging import get_logger
from tools.general_tools import (
    extract_conversation,
    extract_tool_messages,
    get_config_value,
    write_config_value,
)
from tools.price_tools import add_no_trade_record

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()


class BaseAgent:
    """
    Base class for trading agents

    Main functionalities:
    1. MCP tool management and connection
    2. AI agent creation and configuration
    3. Trading execution and decision loops
    4. Logging and management
    5. Position and configuration management
    """

    # Default NASDAQ 100 stock symbols
    DEFAULT_STOCK_SYMBOLS = [
        "NVDA",
        "MSFT",
        "AAPL",
        "GOOG",
        "GOOGL",
        "AMZN",
        "META",
        "AVGO",
        "TSLA",
        "NFLX",
        "PLTR",
        "COST",
        "ASML",
        "AMD",
        "CSCO",
        "AZN",
        "TMUS",
        "MU",
        "LIN",
        "PEP",
        "SHOP",
        "APP",
        "INTU",
        "AMAT",
        "LRCX",
        "PDD",
        "QCOM",
        "ARM",
        "INTC",
        "BKNG",
        "AMGN",
        "TXN",
        "ISRG",
        "GILD",
        "KLAC",
        "PANW",
        "ADBE",
        "HON",
        "CRWD",
        "CEG",
        "ADI",
        "ADP",
        "DASH",
        "CMCSA",
        "VRTX",
        "MELI",
        "SBUX",
        "CDNS",
        "ORLY",
        "SNPS",
        "MSTR",
        "MDLZ",
        "ABNB",
        "MRVL",
        "CTAS",
        "TRI",
        "MAR",
        "MNST",
        "CSX",
        "ADSK",
        "PYPL",
        "FTNT",
        "AEP",
        "WDAY",
        "REGN",
        "ROP",
        "NXPI",
        "DDOG",
        "AXON",
        "ROST",
        "IDXX",
        "EA",
        "PCAR",
        "FAST",
        "EXC",
        "TTWO",
        "XEL",
        "ZS",
        "PAYX",
        "WBD",
        "BKR",
        "CPRT",
        "CCEP",
        "FANG",
        "TEAM",
        "CHTR",
        "KDP",
        "MCHP",
        "GEHC",
        "VRSK",
        "CTSH",
        "CSGP",
        "KHC",
        "ODFL",
        "DXCM",
        "TTD",
        "ON",
        "BIIB",
        "LULU",
        "CDW",
        "GFS",
    ]

    def __init__(
        self,
        signature: str,
        basemodel: str,
        asset_type: str = "stock",
        stock_symbols: Optional[List[str]] = None,
        mcp_config: Optional[Dict[str, Dict[str, Any]]] = None,
        log_path: Optional[str] = None,
        max_steps: int = 10,
        max_retries: int = 3,
        base_delay: float = 0.5,
        openai_base_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        initial_cash: float = 10000.0,
        init_date: str = "2025-10-13",
        trade_style: str = "swing",
    ):
        """
        Initialize BaseAgent

        Args:
            signature: Agent signature/name
            basemodel: Base model name
            stock_symbols: List of stock symbols, defaults to NASDAQ 100
            mcp_config: MCP tool configuration, including port and URL information
            log_path: Log path, defaults to ./data/agent_data
            max_steps: Maximum reasoning steps
            max_retries: Maximum retry attempts
            base_delay: Base delay time for retries
            openai_base_url: OpenAI API base URL
            openai_api_key: OpenAI API key
            initial_cash: Initial cash amount
            init_date: Initialization date
        """
        self.signature = signature
        self.basemodel = basemodel
        self.asset_type = asset_type
        self.stock_symbols = stock_symbols or self.DEFAULT_STOCK_SYMBOLS
        self.trade_style = trade_style.lower() if trade_style else "swing"
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.initial_cash = initial_cash
        self.init_date = init_date

        # Set MCP configuration
        self.mcp_config = mcp_config or self._get_default_mcp_config()

        # Set log path
        self.base_log_path = log_path or "./data/agent_data"

        # Determine provider from basemodel or openai_base_url
        is_deepseek = "deepseek" in basemodel.lower()
        is_groq = "groq" in basemodel.lower() or (openai_base_url and "groq" in openai_base_url.lower())
        is_gpt = "gpt" in basemodel.lower() or "4o" in basemodel.lower()
        is_claude = "claude" in basemodel.lower()

        # Set API configuration based on provider
        if openai_api_key == None:
            # Use provider-specific API key based on detected provider
            if is_deepseek:
                self.openai_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
                print(f"🔑 Using DeepSeek API key")
            elif is_groq:
                self.openai_api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
                print(f"🔑 Using Groq API key")
            elif is_gpt:
                self.openai_api_key = os.getenv("OPENAI_API_KEY")
                print(f"🔑 Using OpenAI API key")
            else:
                self.openai_api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.openai_api_key = openai_api_key

        if openai_base_url == None:
            # Use provider-specific API base URL based on model
            if is_deepseek:
                self.openai_base_url = os.getenv("DEEPSEEK_API_BASE") or "https://api.deepseek.com/v1"
            elif is_groq:
                self.openai_base_url = os.getenv("GROQ_API_BASE") or "https://api.groq.com/openai/v1"
            elif is_gpt:
                self.openai_base_url = os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
            else:
                self.openai_base_url = os.getenv("OPENAI_API_BASE")
        else:
            self.openai_base_url = openai_base_url

        # Initialize components
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: Optional[List] = None
        self.model: Optional[ChatOpenAI] = None
        self.agent: Optional[Any] = None

        # Data paths
        self.data_path = os.path.join(self.base_log_path, self.signature)
        self.position_file = os.path.join(self.data_path, "position", "position.jsonl")

    def _get_default_mcp_config(self) -> Dict[str, Dict[str, Any]]:
        """Get default MCP configuration"""
        if os.getenv("GITHUB_ACTIONS") == "true":
            # Use service names for GitHub Actions environment
            if self.asset_type == "futures":
                # Futures uses prices-service and futures-trade-service
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://math-service:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "crypto_local": {
                        "transport": "streamable_http",
                        "url": f"http://prices-service:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://search-service:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "futures_trade": {
                        "transport": "streamable_http",
                        "url": f"http://futures-trade-service:{os.getenv('FUTURES_TRADE_HTTP_PORT', '8005')}/mcp",
                    },
                }
            elif self.asset_type == "crypto":
                # Crypto uses prices-service and crypto-trade-service
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://math-service:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "crypto_local": {
                        "transport": "streamable_http",
                        "url": f"http://prices-service:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://search-service:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "crypto_trade": {
                        "transport": "streamable_http",
                        "url": f"http://crypto-trade-service:{os.getenv('CRYPTO_TRADE_HTTP_PORT', '8004')}/mcp",
                    },
                }
            else:
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://math-service:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "stock_local": {
                        "transport": "streamable_http",
                        "url": f"http://prices-service:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://search-service:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "trade": {
                        "transport": "streamable_http",
                        "url": f"http://trade-service:{os.getenv('TRADE_HTTP_PORT', '8002')}/mcp",
                    },
                }
        else:
            # Use host.docker.internal for local development
            if self.asset_type == "futures":
                # Futures uses prices-service and futures-trade-service
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "crypto_local": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "futures_trade": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('FUTURES_TRADE_HTTP_PORT', '8005')}/mcp",
                    },
                }
            elif self.asset_type == "crypto":
                # Crypto uses prices-service and crypto-trade-service
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "crypto_local": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "crypto_trade": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('CRYPTO_TRADE_HTTP_PORT', '8004')}/mcp",
                    },
                }
            else:
                return {
                    "math": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
                    },
                    "stock_local": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
                    },
                    "search": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
                    },
                    "trade": {
                        "transport": "streamable_http",
                        "url": f"http://host.docker.internal:{os.getenv('TRADE_HTTP_PORT', '8002')}/mcp",
                    },
                }

    async def initialize(self) -> None:
        """Initialize MCP client and AI model"""
        print(f"🚀 Initializing agent: {self.signature}")

        # Validate OpenAI configuration
        if not self.openai_api_key:
            raise ValueError(
                "❌ OpenAI API key not set. Please configure OPENAI_API_KEY in environment or config file."
            )
        if not self.openai_base_url:
            print("⚠️  OpenAI base URL not set, using default")

        try:
            # Create MCP client
            print(f"MCP config: {self.mcp_config}")
            self.client = MultiServerMCPClient(self.mcp_config)

            # Get tools
            self.tools = await self.client.get_tools()
            if not self.tools:
                print(
                    "⚠️  Warning: No MCP tools loaded. MCP services may not be running."
                )
                print(f"   MCP configuration: {self.mcp_config}")
            else:
                print(f"✅ Loaded {len(self.tools)} MCP tools")
        except Exception as e:
            print(f"❌ Error during MCP client initialization: {e}")
            raise RuntimeError(
                f"❌ Failed to initialize MCP client: {e}\n"
                f"   Please ensure MCP services are running at the configured ports.\n"
                f"   Run: python agent_tools/start_mcp_services.py"
            )

        try:
            # Create AI model based on provider
            if "claude" in self.basemodel.lower():
                # Use ChatAnthropic for Claude models
                print(f"🤖 Using Claude model: {self.basemodel}")
                self.model = ChatAnthropic(
                    model=self.basemodel.split("/")[
                        -1
                    ],  # Extract model name (e.g., claude-3.5-sonnet)
                    api_key=self.openai_api_key,  # Use OPENAI_API_KEY env var which should contain Claude key
                    max_retries=3,
                    timeout=30,
                )
            else:
                # Use ChatOpenAI for other models
                self.model = ChatOpenAI(
                    model=self.basemodel,
                    base_url=self.openai_base_url,
                    api_key=self.openai_api_key,
                    max_retries=3,
                    timeout=30,
                )
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize AI model: {e}")

        # Note: agent will be created in run_trading_session() based on specific date
        # because system_prompt needs the current date and price information

        print(f"✅ Agent {self.signature} initialization completed")

    def _setup_logging(self, today_date: str) -> str:
        """Set up log file path"""
        log_path = os.path.join(self.base_log_path, self.signature, "log", today_date)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return os.path.join(log_path, "log.jsonl")

    def _log_message(self, log_file: str, new_messages: List[Dict[str, str]]) -> None:
        """Log messages to log file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "signature": self.signature,
            "new_messages": new_messages,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    async def _ainvoke_with_retry(self, message: List[Dict[str, str]]) -> Any:
        """Agent invocation with retry"""
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.agent.ainvoke(
                    {"messages": message}, {"recursion_limit": 100}
                )
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                print(
                    f"⚠️ Attempt {attempt} failed, retrying after {self.base_delay * attempt} seconds..."
                )
                print(f"Error details: {e}")
                await asyncio.sleep(self.base_delay * attempt)

    async def run_trading_session(self, today_date: str) -> None:
        """
        Run single day trading session

        Args:
            today_date: Trading date
        """
        # Initialize enhanced logger
        logger = get_logger()
        logger.header(f"Trading Session: {today_date}")
        logger.info(f"Trading {len(self.stock_symbols)} assets: {', '.join(self.stock_symbols)}")

        print(f"📈 Starting trading session: {today_date}")

        # Set up logging
        log_file = self._setup_logging(today_date)

        # Update system prompt
        if self.asset_type == "crypto":
            system_prompt = get_crypto_agent_system_prompt(today_date, self.signature)
            system_prompt = system_prompt.replace("__TOOL_NAMES__", "{tool_names}")
            system_prompt = system_prompt.replace("__TOOLS__", "{tools}")
        elif self.asset_type == "futures":
            system_prompt = get_futures_agent_system_prompt(today_date, self.signature, self.trade_style)
            system_prompt = system_prompt.replace("__TOOL_NAMES__", "{tool_names}")
            system_prompt = system_prompt.replace("__TOOLS__", "{tools}")
        else:
            system_prompt = get_agent_system_prompt(today_date, self.signature)

        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=system_prompt,
        )

        # Initial user query
        user_query = [
            {
                "role": "user",
                "content": f"Please analyze and update today's ({today_date}) positions.",
            }
        ]
        message = user_query.copy()

        # Log initial message
        self._log_message(log_file, user_query)

        # Trading loop
        current_step = 0
        total_trades = 0
        while current_step < self.max_steps:
            current_step += 1
            logger.step(current_step, self.max_steps)
            print(f"\n{'='*70}")
            print(f"🔄 STEP {current_step}/{self.max_steps}")
            print(f"{'='*70}")

            try:
                # Call agent
                response = await self._ainvoke_with_retry(message)

                # Extract agent response
                agent_response = extract_conversation(response, "final")

                # Log agent thinking
                if agent_response:
                    logger.thinking(agent_response)
                    print("\n📝 Agent Response Summary:")
                    # Show first 200 chars of response
                    summary = agent_response[:300] + ("..." if len(agent_response) > 300 else "")
                    print(f"   {summary}")

                # Check stop signal
                if STOP_SIGNAL in agent_response:
                    logger.success("Stop signal detected, trading session ended")
                    print("✅ Received stop signal, trading session ended")
                    print(agent_response)
                    self._log_message(
                        log_file, [{"role": "assistant", "content": agent_response}]
                    )
                    break

                # Extract tool messages
                tool_msgs = extract_tool_messages(response)

                # Log tool results
                if tool_msgs:
                    print(f"\n🔧 Tool Results ({len(tool_msgs)} tools called):")
                    for i, msg in enumerate(tool_msgs, 1):
                        content = msg.content if hasattr(msg, 'content') else str(msg)
                        print(f"   [{i}] {content[:200]}..." if len(content) > 200 else f"   [{i}] {content}")
                        logger.tool_result("Agent Tool", content, success=True)
                else:
                    print("\n   ℹ️  No tool calls in this step")

                tool_response = "\n".join([msg.content for msg in tool_msgs])

                # Prepare new messages
                new_messages = [
                    {"role": "assistant", "content": agent_response},
                    {"role": "user", "content": f"Tool results: {tool_response}"},
                ]

                # Add new messages
                message.extend(new_messages)

                # Log messages
                self._log_message(log_file, new_messages[0])
                self._log_message(log_file, new_messages[1])

            except Exception as e:
                logger.error(f"Trading step {current_step} failed: {str(e)}", "TradingStepError")
                print(f"❌ Trading session error: {str(e)}")
                print(f"Error details: {e}")
                raise

        # Handle trading results
        await self._handle_trading_result(today_date)

        # Log session summary
        logger.execution_summary(
            date=today_date,
            status="success",
            trades_made=total_trades,
            p_and_l=0.0,  # Calculate from position file if available
            total_cost=0.0,  # Will be populated from API calls
            total_tokens=0  # Will be populated from API calls
        )

    async def _handle_trading_result(self, today_date: str) -> None:
        """Handle trading results"""
        if_trade = get_config_value("IF_TRADE")
        if if_trade:
            write_config_value("IF_TRADE", False)
            print("✅ Trading completed")
        else:
            print("📊 No trading, maintaining positions")
            try:
                add_no_trade_record(today_date, self.signature)
            except NameError as e:
                print(f"❌ NameError: {e}")
                raise
            write_config_value("IF_TRADE", False)

    def register_agent(self) -> None:
        """Register new agent, create initial positions"""
        # Check if position.jsonl file already exists
        if os.path.exists(self.position_file):
            print(
                f"⚠️ Position file {self.position_file} already exists, skipping registration"
            )
            return

        # Ensure directory structure exists
        position_dir = os.path.join(self.data_path, "position")
        if not os.path.exists(position_dir):
            os.makedirs(position_dir)
            print(f"📁 Created position directory: {position_dir}")

        # Create initial positions
        init_position = {symbol: 0 for symbol in self.stock_symbols}
        init_position["CASH"] = self.initial_cash

        with open(
            self.position_file, "w"
        ) as f:  # Use "w" mode to ensure creating new file
            f.write(
                json.dumps(
                    {"date": self.init_date, "id": 0, "positions": init_position}
                )
                + "\n"
            )

        print(f"✅ Agent {self.signature} registration completed")
        print(f"📁 Position file: {self.position_file}")
        print(f"💰 Initial cash: ${self.initial_cash}")
        print(f"📊 Number of stocks: {len(self.stock_symbols)}")

    def get_trading_dates(self, init_date: str, end_date: str) -> List[str]:
        """
        Get trading date list

        Args:
            init_date: Start date
            end_date: End date

        Returns:
            List of trading dates
        """
        dates = []
        max_date = None

        if not os.path.exists(self.position_file):
            self.register_agent()
            max_date = init_date
        else:
            # Read existing position file, find latest date
            with open(self.position_file, "r") as f:
                for line in f:
                    doc = json.loads(line)
                    current_date = doc["date"]
                    if max_date is None:
                        max_date = current_date
                    else:
                        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d")
                        max_date_obj = datetime.strptime(max_date, "%Y-%m-%d")
                        if current_date_obj > max_date_obj:
                            max_date = current_date

        # Check if new dates need to be processed
        max_date_obj = datetime.strptime(max_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_obj <= max_date_obj:
            return []

        # Generate trading date list
        trading_dates = []
        current_date = max_date_obj + timedelta(days=1)

        while current_date <= end_date_obj:
            # For crypto and futures, trade 24/7; for stocks, trade on weekdays only
            if self.asset_type == "crypto" or self.asset_type == "futures" or current_date.weekday() < 5:
                trading_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        return trading_dates

    async def run_with_retry(self, today_date: str) -> None:
        """Run method with retry"""
        for attempt in range(1, self.max_retries + 1):
            try:
                print(
                    f"🔄 Attempting to run {self.signature} - {today_date} (Attempt {attempt})"
                )
                await self.run_trading_session(today_date)
                print(f"✅ {self.signature} - {today_date} run successful")
                return
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {str(e)}")
                if attempt == self.max_retries:
                    print(f"💥 {self.signature} - {today_date} all retries failed")
                    raise
                else:
                    wait_time = self.base_delay * attempt
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)

    async def run_hourly_trading_session(self, today_date: str, hour: int) -> None:
        """
        Run single hour trading session

        Args:
            today_date: Trading date
            hour: Trading hour
        """
        # Initialize enhanced logger
        logger = get_logger()
        logger.header(f"Trading Session: {today_date} {hour}:00")
        logger.info(f"Trading {len(self.stock_symbols)} assets: {', '.join(self.stock_symbols)}")

        print(f"📈 Starting trading session: {today_date} {hour}:00")

        # Set up logging
        log_file = self._setup_logging(f"{today_date}_{hour}")

        # Update system prompt
        if self.asset_type == "crypto":
            system_prompt = get_crypto_agent_system_prompt(today_date, self.signature)
            system_prompt = system_prompt.replace("__TOOL_NAMES__", "{tool_names}")
            system_prompt = system_prompt.replace("__TOOLS__", "{tools}")
        elif self.asset_type == "futures":
            system_prompt = get_hourly_futures_agent_system_prompt(today_date, self.signature, self.trade_style, hour)
            system_prompt = system_prompt.replace("__TOOL_NAMES__", "{tool_names}")
            system_prompt = system_prompt.replace("__TOOLS__", "{tools}")
        else:
            system_prompt = get_agent_system_prompt(today_date, self.signature)

        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=system_prompt,
        )

        # Initial user query
        user_query = [
            {
                "role": "user",
                "content": f"Please analyze and update today's ({today_date}) positions for the {hour}:00 hour.",
            }
        ]
        message = user_query.copy()

        # Log initial message
        self._log_message(log_file, user_query)

        # Trading loop
        current_step = 0
        total_trades = 0
        while current_step < self.max_steps:
            current_step += 1
            logger.step(current_step, self.max_steps)
            print(f"\n{'='*70}")
            print(f"🔄 STEP {current_step}/{self.max_steps}")
            print(f"{'='*70}")

            try:
                # Call agent
                response = await self._ainvoke_with_retry(message)

                # Extract agent response
                agent_response = extract_conversation(response, "final")

                # Log agent thinking
                if agent_response:
                    logger.thinking(agent_response)
                    print("\n📝 Agent Response Summary:")
                    # Show first 200 chars of response
                    summary = agent_response[:300] + ("..." if len(agent_response) > 300 else "")
                    print(f"   {summary}")

                # Check stop signal
                if STOP_SIGNAL in agent_response:
                    logger.success("Stop signal detected, trading session ended")
                    print("✅ Received stop signal, trading session ended")
                    print(agent_response)
                    self._log_message(
                        log_file, [{"role": "assistant", "content": agent_response}]
                    )
                    break

                # Extract tool messages
                tool_msgs = extract_tool_messages(response)

                # Log tool results
                if tool_msgs:
                    print(f"\n🔧 Tool Results ({len(tool_msgs)} tools called):")
                    for i, msg in enumerate(tool_msgs, 1):
                        content = msg.content if hasattr(msg, 'content') else str(msg)
                        print(f"   [{i}] {content[:200]}..." if len(content) > 200 else f"   [{i}] {content}")
                        logger.tool_result("Agent Tool", content, success=True)
                else:
                    print("\n   ℹ️  No tool calls in this step")

                tool_response = "\n".join([msg.content for msg in tool_msgs])

                # Prepare new messages
                new_messages = [
                    {"role": "assistant", "content": agent_response},
                    {"role": "user", "content": f"Tool results: {tool_response}"},
                ]

                # Add new messages
                message.extend(new_messages)

                # Log messages
                self._log_message(log_file, new_messages[0])
                self._log_message(log_file, new_messages[1])

            except Exception as e:
                logger.error(f"Trading step {current_step} failed: {str(e)}", "TradingStepError")
                print(f"❌ Trading session error: {str(e)}")
                print(f"Error details: {e}")
                raise

        # Handle trading results
        await self._handle_trading_result(today_date)

        # Log session summary
        logger.execution_summary(
            date=today_date,
            status="success",
            trades_made=total_trades,
            p_and_l=0.0,  # Calculate from position file if available
            total_cost=0.0,  # Will be populated from API calls
            total_tokens=0  # Will be populated from API calls
        )

    async def run_date_range(self, init_date: str, end_date: str) -> None:
        """
        Run all trading days in date range

        Args:
            init_date: Start date
            end_date: End date
        """
        print(f"📅 Running date range: {init_date} to {end_date}")

        # Get trading date list
        trading_dates = self.get_trading_dates(init_date, end_date)

        if not trading_dates:
            print(f"ℹ️ No trading days to process")
            return

        print(f"📊 Trading days to process: {trading_dates}")

        # Process each trading day
        for date in trading_dates:
            for hour in range(9, 17):
                print(f"🔄 Processing {self.signature} - Date: {date} Hour: {hour}")

                # Set configuration
                write_config_value("TODAY_DATE", date)
                write_config_value("SIGNATURE", self.signature)

                try:
                    await self.run_hourly_trading_session(date, hour)
                except Exception as e:
                    print(f"❌ Error processing {self.signature} - Date: {date} Hour: {hour}")
                    print(e)
                    raise

        print(f"✅ {self.signature} processing completed")

    def get_position_summary(self) -> Dict[str, Any]:
        """Get position summary"""
        if not os.path.exists(self.position_file):
            return {"error": "Position file does not exist"}

        positions = []
        with open(self.position_file, "r") as f:
            for line in f:
                positions.append(json.loads(line))

        if not positions:
            return {"error": "No position records"}

        latest_position = positions[-1]
        return {
            "signature": self.signature,
            "latest_date": latest_position.get("date"),
            "positions": latest_position.get("positions", {}),
            "total_records": len(positions),
        }

    def __str__(self) -> str:
        return f"BaseAgent(signature='{self.signature}', basemodel='{self.basemodel}', stocks={len(self.stock_symbols)})"

    def __repr__(self) -> str:
        return self.__str__()
