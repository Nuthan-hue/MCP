#!/bin/bash
uvicorn servers.llm_server:app --host 0.0.0.0 --port 8000
