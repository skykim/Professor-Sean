using UnityEngine;
using UnityEngine.Networking;
using System.Threading.Tasks;
using System.Text;
using Newtonsoft.Json;
using ReadyPlayerMe.Core;

public class ElevenLabsManager : MonoBehaviour
{    
    [SerializeField] private string voice_id = "";
    [SerializeField] private string API_KEY = "";
    private string API_URL = "https://api.elevenlabs.io/v1/text-to-speech/";

    [System.Serializable]
    public class VoiceSettings
    {
        public float stability { get; set; }
        public float similarity_boost { get; set; }
    }

    public VoiceHandler handler;

    [System.Serializable]
    public class VoiceRequest
    {
        public string text { get; set; }
        public string model_id { get; set; }
        public VoiceSettings voice_settings { get; set; }
    }

    public async Task<AudioClip> InvokeVoiceCloning(string query)
    {
        // Create request object
        var voiceRequest = new VoiceRequest
        {
            text = query,
            model_id = "eleven_multilingual_v2",
            voice_settings = new VoiceSettings
            {
                stability = 0.5f,
                similarity_boost = 0.5f
            }
        };

        // Serialize to JSON
        string jsonString = JsonConvert.SerializeObject(voiceRequest);
        byte[] jsonBytes = Encoding.UTF8.GetBytes(jsonString);

        using (UnityWebRequest request = new UnityWebRequest(API_URL + voice_id, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(jsonBytes);
            request.downloadHandler = new DownloadHandlerAudioClip(API_URL + voice_id, AudioType.MPEG);
            
            // Set headers
            request.SetRequestHeader("Accept", "audio/mpeg");
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("xi-api-key", API_KEY);

            try
            {
                // Send request
                await request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    AudioClip audioClip = DownloadHandlerAudioClip.GetContent(request);
                    return audioClip;
                }
                else
                {
                    Debug.LogError($"API Error: {request.error}");
                    Debug.LogError($"Response Code: {request.responseCode}");
                    Debug.LogError($"Response: {request.downloadHandler.text}");
                    return null;
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Exception occurred: {e.Message}");
                return null;
            }
        }
    }

    public async void TextToSpeech(string query)
    {
        AudioClip generatedAudio = await InvokeVoiceCloning(query);
        if(generatedAudio != null)
        {
            handler.PlayAudioClip(generatedAudio);
        }
    }     
}