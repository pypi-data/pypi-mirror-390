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
- **Desktop Notifications**: Display beautiful notification messages

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
### Desktop Notifications
```
# Show notification message (auto-closes after 3 seconds)
pgzpro.message("Game started!")

# Custom notification with colors and duration
pgzpro.message("Level completed!", text_color="white", bg_color="green", duration=5.0)

# Quick notification (1 second)
pgzpro.message("Item collected!", duration=1.0)
```
## ⚠️ AI generation needs active internet connection

## 🆕 What's New in Version 1.1.0
- **Notification System**: Added new message() function for desktop notifications
- **Correction of defects**: Fixed cleaning of temporary files

## 📦 Installation

```bash
pip install pgzpro
```

## 🔄 Updating the Library

```bash
pip install -U pgzpro
```
### or
```bash
pip install --upgrade pgzpro
```