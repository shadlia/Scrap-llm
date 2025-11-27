# Makefile for Scrap LLM project

# Colors for terminal output
CYAN=\033[0;36m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m # No Color

.PHONY: all install install-backend install-frontend start-backend start-frontend dev test-api

# Default target: show help
all: install-docker install-frontend start-docker start-frontend

# Install all dependencies
install: install-backend install-frontend
	@echo "${GREEN}All dependencies installed!${NC}"

# Install backend dependencies
install-backend:
	@echo "${CYAN}Installing backend dependencies...${NC}"
	@cd backend && python -m poetry install
	@echo "${GREEN}Backend dependencies installed!${NC}"

# Install frontend dependencies
install-frontend:
	@echo "${CYAN}Installing frontend dependencies...${NC}"
	@cd frontend && npm install
	@echo "${GREEN}Frontend dependencies installed!${NC}"

# Install docker
install-docker:
	@echo "${CYAN}Building docker containers...${NC}"
	@docker compose build
	@echo "${GREEN}Docker containers built!${NC}"

# Start the backend service
start-backend:
	@echo "${CYAN}Starting backend server...${NC}"
	@cd backend && set "LOCAL_DEV=local" && python -m poetry run serve

# Start the frontend service
start-frontend:
	@echo "${CYAN}Starting frontend development server...${NC}"
	@cd frontend && set "LOCAL_DEV=local" && npm run dev -- -p 3001

start-docker:
	@echo "${CYAN}Starting docker containers...${NC}"
	@set "LOCAL_DEV=docker" && docker compose up -d
	@echo "${GREEN}Docker containers started!${NC}"

stop-docker:
	@echo "${CYAN}Stopping docker containers...${NC}"
	@docker compose down
	@echo "${GREEN}Docker containers stopped!${NC}"

