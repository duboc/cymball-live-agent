# Memory Bank: Live Food Agent - Comida Rápida Fantástica

## Overview
This memory bank contains comprehensive documentation for the **Live Food Agent** project - an AI-powered customer service system featuring **Félix, tu Amigo del Sabor**, a Spanish-speaking virtual assistant for fast food ordering.

## Memory Bank Structure

### Core Documentation Files

#### 📋 [Project Brief](./projectbrief.md)
**Foundation document** - Project goals, objectives, and core purpose
- Business and technical objectives
- Target users and success metrics
- Key differentiators and constraints

#### 🏪 [Product Context](./productContext.md) 
**Business context** - Why this project exists and how it should work
- Brand identity and restaurant personality
- Félix character profile and communication style
- User experience design and value propositions

#### ⚙️ [System Patterns](./systemPatterns.md)
**Technical architecture** - How the system is designed and structured
- Agent-based architecture patterns
- Communication and data flow patterns
- Critical system components and scalability considerations

#### 💻 [Tech Context](./techContext.md)
**Technology stack** - Tools, frameworks, and development setup
- Backend/frontend technologies and AI components
- Development environment and API configuration
- Performance considerations and integration points

#### 🎯 [Active Context](./activeContext.md)
**Current state** - What's happening now and immediate focus areas
- Current development priorities and technical decisions
- Active insights, learnings, and working assumptions
- Known constraints and success metrics

#### 📊 [Progress](./progress.md)
**Status tracking** - What's working, what's in progress, what's next
- Detailed breakdown of completed features
- Known issues and technical debt
- Evolution of project decisions and next milestones

## Quick Reference

### Project Status: **Feature-Complete MVP**
- ✅ Core ordering functionality working
- ✅ Félix AI agent fully operational
- 🔄 Audio system components implemented, may need optimization
- 🚧 Production deployment requires database migration

### Key Technologies
- **Backend**: FastAPI + Python + WebSocket
- **AI**: Google Gemini Live 2.5 Flash + ADK Framework
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Audio**: Web Audio API + PCM Streaming

### Character: Félix, tu Amigo del Sabor
- **Language**: Spanish (es-ES) exclusively
- **Personality**: Enthusiastic, helpful, friendly
- **Strategy**: Combo-driven sales with proactive upselling
- **Voice**: "Leda" for audio interactions

### Architecture Pattern
```
Web Client ↔ FastAPI Server ↔ Google Gemini Live
     ↓              ↓              ↓
Menu System   Tool Functions   AI Agent
```

## Development Context

### Current Working Directory
```
/Users/duboc/local/projects/live-food-agent/
├── app/                    # Main application
│   ├── main.py            # FastAPI server
│   ├── food/              # Agent and business logic
│   └── static/            # Frontend interface
├── memory-bank/           # This documentation
├── requirements.txt       # Dependencies
└── setup_venv.sh         # Environment setup
```

### Quick Start
```bash
cd /Users/duboc/local/projects/live-food-agent
source venv/bin/activate
cd app
uvicorn main:app --reload
# Access: http://localhost:8000
```

### Key Files to Know
- `app/food/agent.py` - Félix agent configuration
- `app/food/tools/prompts.py` - Félix personality and instructions
- `app/food/tools/tools.py` - Business logic and menu system
- `app/main.py` - Server and WebSocket handling
- `app/static/index.html` - Three-column user interface

## Next Development Priorities

### 1. Production Readiness (Immediate)
- Database migration from in-memory storage
- Proper session management with unique IDs
- Error handling and resilience improvements

### 2. Audio System Optimization (Short-term)
- Latency reduction for voice interactions
- Browser compatibility testing
- Audio quality optimization

### 3. User Experience Enhancements (Medium-term)
- Mobile responsive design
- Payment integration
- Advanced ordering features

## Using This Memory Bank

### When Starting New Work
1. **Always read** `activeContext.md` for current focus
2. **Check** `progress.md` for latest status
3. **Reference** `systemPatterns.md` for technical approach
4. **Update** relevant files after significant changes

### When Making Changes
- Update `activeContext.md` with new developments
- Document decisions and learnings in relevant files
- Keep `progress.md` current with status changes
- Note any architecture changes in `systemPatterns.md`

### For New Team Members
- Start with `projectbrief.md` for project understanding
- Read `productContext.md` for business context
- Review `techContext.md` for development setup
- Use `progress.md` to understand current capabilities

## Memory Bank Maintenance

This memory bank should be updated when:
- Making significant code changes
- Discovering new patterns or insights
- Changing technical approaches
- Completing major milestones
- User requests **"update memory bank"**

The memory bank serves as the complete context for continuing work on this project after any interruption or session reset.

---

**Project Status**: Active Development | **Last Updated**: January 5, 2025 | **Version**: MVP Complete
