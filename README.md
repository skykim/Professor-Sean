# Professor-Sean
Sogang Full Stack RAG Project

## Requirements ##
- Unity 2023.2.20f1
- Sentis 1.5.0-pre.3

## Setup (Python) ##

### 1. Install requirements ###

```
pip install -r requirements.txt
```

### 2. Launch RestAPI server ###

```
python main_flask.py
```

## Setup (Unity) ##

### 1. Download and Extract StreamingAssets.zip to the /Assets/StreamingAssets Folder ###
- Download [StreamingAssets.zip](https://drive.google.com/file/d/1T6LUoh4jd6EAB6_97-85GVsnGUCodSUj/view?usp=sharing)
- Extract it to the /Assets/StreamingAssets folder

### 2. Train Your Voice and Obtain an API Key from ElevenLabs ###
- Get your API Key: ElevenLabs > Settings > [API KEYS](https://elevenlabs.io/app/settings/api-keys)
- Get your Voice ID: ElevenLabs > Voices >  [ID](https://elevenlabs.io/app/voice-lab)

### 3. Enter Your Voice ID and API Key ###
- Select the Professor-Sean scene and find ElevenLabsManager in the Hierarchy window
- Enter your Voice ID and API Key in the Inspector window
