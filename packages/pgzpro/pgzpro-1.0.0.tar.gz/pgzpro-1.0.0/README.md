# PGZPro - AI-Powered Game Development Toolkit

A powerful Python library that combines AI image generation with Pygame Zero enhancements. Create stunning games with AI-generated assets and streamlined development workflow.

## 🚀 Features

### AI Image Generation
- **Flux Model Integration**: Generate high-quality images using G4F's Flux AI model
- **Smart Prompt Translation**: Automatic translation of non-English prompts
- **Transparent Backgrounds**: Create PNG images with transparent backgrounds
- **Custom Dimensions**: Generate images in any size up to 1024x1024 pixels

### Pygame Zero Enhancements
- **Window Centering**: Automatically center your game window on any screen
- **Seamless Integration**: Works perfectly with Pygame Zero ecosystem

## 🛠️ Core Commands

### Window Management
```
import pgzpro  # MUST be imported BEFORE pgzrun

pgzpro.center()           # Center the game window on screen
pgzpro.no_logging(True)   # Disable debug logging (optional)

import pgzrun
```
### AI Asset Generation
```
# Generate game background (automatically fits screen)
background = pgzpro.bg_generate("fantasy forest with mountains")

# Generate character with transparent background
character = pgzpro.actor_generate("hero knight", "60x80")

# Generate game objects
crystal = pgzpro.actor_generate("magic crystal", "40x40")
```
## ⚠️ AI generation needs active internet connection

## 📦 Installation

```bash
pip install pgzpro
```
