#!/bin/bash
uvicorn servers.email_server:app --host 0.0.0.0 --port 8000
