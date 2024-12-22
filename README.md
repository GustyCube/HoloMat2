# HoloMat2

## Home Screen Application

## Overview
This Home Screen application is a Pygame-based user interface that allows users to navigate through different apps displayed as circular icons. The app features an interactive main menu where the main home button toggles the visibility of app icons. Users can select and launch these apps by clicking on them.

## Features
- **Home Circle Toggle**: Tap the main circle to reveal or hide the app icons.
- **Animated App Icons**: Smooth animations when toggling the visibility of app circles.
- **Dynamic App Launch**: Click on an app circle to launch the corresponding app.
- **Interactive Touch Mapping**: Supports capacitive touch input with custom coordinate mapping for better touch accuracy.
- **Audio Feedback**: Provides audio feedback for different actions (like tapping the home button or selecting an app).

## Requirements

- **Python 3.10+**
- **Libraries**:
  - `pygame==2.5.0`
  - `python-dotenv==1.0.0`

You can install all dependencies using the following command:
pip install -r requirements.txt



2. **Home Screen Navigation**:
- Tap the **main home circle** to toggle the visibility of app circles.
- Tap an **app circle** to launch the corresponding app.

3. **Touch Screen Input**:
- Touch screen input is mapped using the `map_coords(x, y)` function to ensure accurate alignment with the display.

4. **Exiting**:
- Close the application window to exit.

## How It Works

### **Main Home Circle**
- The central main circle serves as a toggle button. When tapped, it animates the app circles to appear or disappear.

### **App Circles**
- Up to 8 app circles are displayed around the main circle. Each circle can be clicked to launch its respective app.
- When hovered, the circle's size increases slightly, providing a hover effect.

### **Touch Mapping**
- Touch inputs from capacitive touch screens are mapped to the display using the `map_coords()` function. This ensures the touch points are aligned with the display.

### **Animations**
- The app circles smoothly animate to their final positions when toggled.

### **Audio Feedback**
- Different sounds play for key actions:
- **Startup Sound**: Plays on app launch.
- **Home Button Sound**: Plays when toggling the app menu.
- **Confirmation Sound**: Plays when an app is successfully launched.
- **Reject Sound**: Plays if the app to be launched is not found.

## Customization

### **Add a New App**
1. Create a folder in `apps/` named `app_<index>`, where `<index>` is the next available index.
2. Place the app logic in `app_<index>.py` within the newly created folder.
3. Add an image for the app in `resources/` named `app_<index>.jpg`.

### **Change Sounds**
Replace the files in the `audio/` folder with your own `.wav` files.

### **Customize Circle Positions**
To adjust the position and layout of the circles, modify the `create_circles()` function in `main.py`. The app circle layout is based on polar coordinates relative to the main circle.

## Troubleshooting

### **App Fails to Launch**
- Ensure that the folder and file structure for the app is correct.
- Verify that the `app_<index>.py` file exists in the correct folder.

### **Touch Input Doesn't Match Display**
- Adjust the `map_coords()` function to correctly align touch coordinates with the display.
- I found the touch screen i bought to be inverted and rotated. Yours may not be.

### **Audio Not Playing**
- Make sure the `.wav` files are present in the `audio/` folder.
- Verify that the audio files are not corrupted.

## Future Enhancements
- Add more customizable animations.
- Introduce app preview animations before launch.
- Support multi-touch inputs for advanced interactions.

## License
This project is open-source and free to use for personal or educational purposes.
