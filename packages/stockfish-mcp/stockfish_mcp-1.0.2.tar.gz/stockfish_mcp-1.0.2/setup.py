from setuptools import setup, find_packages

setup(
    packages=["stockfish_mcp", "stockfish_mcp.bin"],
    include_package_data=True,
    package_data={
        "stockfish_mcp.bin": ["*"],
    },
)