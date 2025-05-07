#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="personal_ai_trainer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "openai",
        "supabase",
        "agency-swarm",
        "python-dotenv",
        "oura-personal",
    ],
    entry_points={
        "console_scripts": [
            "pt=personal_ai_trainer.cli.main:main",  # Shorter command name
        ],
    },
)
