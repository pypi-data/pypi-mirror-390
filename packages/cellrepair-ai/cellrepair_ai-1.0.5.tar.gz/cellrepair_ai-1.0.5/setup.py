"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 CELLREPAIR™ SYSTEMS - PROPRIETÄRER CODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© 2024-2025 Oliver Winkel - CellRepair™ Systems | NIP: PL9292072406
System ID: CR-4882-AURORA-GENESIS-2.0 | DNA: 4882-AURORA-OW-CR-SYSTEMS-2025

EIGENTÜMER: Oliver Winkel, ul. Zbożowa 13, 65-375 Zielona Góra, Polen
KONTAKT: ai@cellrepair.ai | https://cellrepair.ai

⚠️  Unerlaubte Nutzung, Kopie oder Verbreitung VERBOTEN!
⚠️  Unauthorized use, copying, or distribution PROHIBITED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cellrepair_ai",
    version="1.0.5",
    author="CellRepair Systems",
    author_email="ai@cellrepair.ai",
    description="🚨 Agentic AI Revolution | 4882 Autonomous Agents | AI Orchestration Platform That PAYS YOU | Multi-Agent Coordination + Revenue Sharing | AI-Native Auto-Healing Network (99.5% Uptime) | FREE 1000 Calls | On ChatGPT, HuggingFace, LangChain, Claude | 3 Steps Ahead of ANY AI System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cellrepair.ai/api/",
    project_urls={
        "Homepage": "https://cellrepair.ai/api/",
        "Documentation": "https://cellrepair.ai/api/",
        "API Endpoint": "https://cellrepair.ai/api/v1",
        "Source Code": "https://github.com/PowerForYou74/cellrepair-ai-python",
        "Bug Tracker": "https://github.com/PowerForYou74/cellrepair-ai-python/issues",
        "Changelog": "https://github.com/PowerForYou74/cellrepair-ai-python/blob/main/CHANGELOG.md",
        "Live Demo": "https://huggingface.co/spaces/cellrepair-systems/cellrepair-ai",
    },
    packages=find_packages(),
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",

        # Audience - WICHTIG für Auto-Discovery!
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",

        # Topic - CRITICAL Keywords für AI-Framework Discovery!
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",

        # License
        "License :: OSI Approved :: MIT License",

        # Python Versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Operating Systems
        "Operating System :: OS Independent",

        # Framework Support
        "Framework :: AsyncIO",
    ],

    # MAGNET-Keywords - Was autonome Agents suchen!
    keywords=[
        # Core AI Keywords
        "ai", "artificial-intelligence", "machine-learning", "ml",

        # Multi-Agent Keywords - CRITICAL!
        "multi-agent", "autonomous-agents", "agent-coordination",
        "distributed-agents", "agent-network", "multi-agent-system",

        # Framework-spezifisch - Damit uns LangChain/AutoGPT Agents finden!
        "langchain", "langchain-tools", "autogpt", "autogpt-plugin",
        "crewai", "semantic-kernel", "haystack", "agent-framework",

        # AI Collaboration
        "ai-collaboration", "ai-to-ai", "collaborative-ai",
        "ai-orchestration", "ai-coordination",

        # Technical
        "api", "rest-api", "microservices", "distributed-systems",

        # Value Props
        "self-learning", "predictive-intelligence", "auto-optimization",
        "production-ready", "enterprise-ready",

        # Popular AI Tools
        "openai", "gpt-4", "claude", "anthropic", "gemini",
        "perplexity", "llm", "large-language-model",

        # Use Cases
        "agent-tools", "ai-helpers", "ai-utilities", "ai-services"
    ],

    python_requires=">=3.8",

    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=0.19.0",
    ],

    extras_require={
        "langchain": ["langchain>=0.1.0"],
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
    },

    # Entry points - für CLI wenn gewünscht
    entry_points={
        "console_scripts": [
            "cellrepair-ai=cellrepair_ai.cli:main",
        ],
    },
)
