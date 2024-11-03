# Professor-Sean
- Professor Sean: RAG-based Lecture Review and Interaction System in Unity
- 2nd Place in Sogang x Upstage Full-Stack LLM Project
- Special Thanks to Soo-Yong Park from Sogang University
- [Slide](https://drive.google.com/file/d/1zYPt_5Q-8SDZpgqIKLU5ICKp9IU7s5bf/view?usp=sharing)

[![Professor Sean](https://img.youtube.com/vi/dfF_bsb1AG8/0.jpg)](https://www.youtube.com/watch?v=dfF_bsb1AG8)

## Requirements ##
- Unity 2023.2.20f1
- Sentis 1.5.0-pre.3

## Setup (Python) ##

### 1. Get an Upstage API Key and Register an Environment Variable ###
- [Upstage Console](https://console.upstage.ai/)
```
UPSTAGE_API_KEY = up_xxxxx
```

### 2. Ingest PDF datasets into Vectorstore (ChromaDB) ###

```
python data_ingestion.py
```

### 3. Launch RestAPI Server ###

```
python main_flask.py
```


## Setup (Unity) ##

### 1. Download and Extract StreamingAssets.zip to the /Assets/StreamingAssets Folder ###
- Download [StreamingAssets.zip](https://drive.google.com/file/d/1T6LUoh4jd6EAB6_97-85GVsnGUCodSUj/view?usp=sharing)
- Extract it to the /Assets/StreamingAssets folder

### 2. Train Your Voice and Obtain an API Key from ElevenLabs ###
- [Get your Voice ID](https://elevenlabs.io/app/voice-lab): ElevenLabs > Voices > ID
- [Get your API Key](https://elevenlabs.io/app/settings/api-keys): ElevenLabs > Settings > API KEYS

### 3. Enter Your Voice ID and API Key ###
- Select the Professor-Sean scene and find ElevenLabsManager in the Hierarchy window
- Enter your Voice ID and API Key in the Inspector window

## Contributors ##
- Sogang University, Graduate Schoold of Metaverse
- Wonyoung Jeong (wonnio98@gmail.com), Jonghwan Bae (bjh0309@gmail.com), Sky Kim (loenahmik@gmail.com)
