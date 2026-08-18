# LibreAvatrak

![License](https://img.shields.io/badge/License-AGPL3.0-blue)
![Front-end](https://img.shields.io/badge/FrontEnd-GodotEngine-green)
![After-end](https://img.shields.io/badge/AfterEnd-PythonFlask-red)
![After-end](https://img.shields.io/badge/AfterEnd-PythonOpenCV-red)
![Version](https://img.shields.io/badge/Version-0.1beta-yellow)

**LibreAvatrak is Free/Libre Software**, licensed under the GNU Affero General Public License v3.

A lightweight single-camera facial motion capture solution built for VTubers and virtual avatar creators.
Powered by MediaPipe to detect face landmarks, calculate head pose (Pitch/Yaw/Roll), and extract expression metrics including EAR eye openness and MAR mouth movement.

## Tech Stack
- **MediaPipe**: Real-time face landmark inference
- **OpenCV**: Camera video capture and image processing
- **Python + Flask**: Multiprocess tracking backend, provides low-latency HTTP data API
- **Godot Engine**: Avatar rendering runtime
- **VRM**: Realtime animation driving for VRM humanoid avatars

Tracking data is streamed to Godot to animate your virtual avatar.
As AGPLv3 software, any modified instance or publicly accessible network service must share source code.

## How To Use
### 1. Ready
Have Python environment, and install Python module from `requirements.txt`
Have Godot Editor. install Godot 4.6

### 2. Run
1. Run Python first.
2. Run Godot second.

### 3. Change Your Character
1. Load your vrm file in Godot and open it as extend scene
2. Copy the all files from the VRM scene to new scene.(The Godot can not visit in read only file)
3. Save new scene as `.scn`(Don't use `.tscn`). And rename as Char.
4. Open the CharShow.scn, delete the old node Char and put your Char.
5. Run it.

## License & Original Intent
LibreAvatrak is licensed under the GNU AGPLv3.
My intention is straightforward: this facial capture tool shall stay free for everyone.
✅ Permitted:
Any individual or creator may run this software free of charge, and earn revenue from content created with this software (such as VTuber streaming, commercial production, etc.).
❌ Not Permitted:
No one may modify the source code, close the source, package and sell this software, or build paid cloud motion capture services based on this project.
If you modify this project and provide its functionality to others over a network, you must fully publish all modified source code.
Architecture note: The facial tracking core runs inside the Flask backend on purpose. This design cooperates with AGPLv3 to prevent proprietary commercial services from being built while evading open-source obligations.
