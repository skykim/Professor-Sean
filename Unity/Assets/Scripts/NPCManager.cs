using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class NPCManager : MonoBehaviour
{
    [SerializeField] private WhisperModel whisperObject;
    [SerializeField] private TMP_InputField inputField;
    [SerializeField] private ElevenLabsManager voiceObject;
    [SerializeField] private GameObject npcTextParent;
    [SerializeField] private GameObject npcTextPrefab;
    [SerializeField] private GameObject userTextPrefab;
    [SerializeField] private ScrollRect dialogueRect;
    
    private bool isWaitingForResponse;
    private const string ApiEndpoint = "http://127.0.0.1:5000/ask";

    private void Awake()
    {
        inputField.onEndEdit.AddListener(OnInputFieldEndEdit);
    }

    async void Start()
    {
        string npcResponse = await SendPromptAsync("hello");
        Debug.Log(npcResponse);
    }
    
    private async void OnInputFieldEndEdit(string text)
    {
        await SendQueryAsync();
    }

    private async Task SendQueryAsync()
    {
        if (isWaitingForResponse) return;

        string inputText = inputField.text;
        if (string.IsNullOrEmpty(inputText)) return;
        
        SetUIState(true);
         
        try
        {
            string userQuery = inputField.text;
            AppendTextPrefab(userTextPrefab, userQuery);

            string npcResponse = await SendPromptAsync(userQuery);
            AppendTextPrefab(npcTextPrefab, npcResponse);
            
            voiceObject.TextToSpeech(npcResponse);
        }
        catch (Exception ex)
        {
            Debug.LogError($"An error occurred: {ex.Message}");
            AppendTextPrefab(npcTextPrefab, "Sorry, an error occurred. Please try again.");
        }
        finally
        {
            SetUIState(false);
        }
    }

    private void SetUIState(bool isProcessing)
    {
        isWaitingForResponse = isProcessing;
        inputField.interactable = !isProcessing;
        
        if(!isProcessing)
            inputField.text = "";
    }
    
    private async Task<string> SendPromptAsync(string promptText)
    {
        using (var client = new HttpClient())
        {
            var requestObject = new
            {
                question = promptText
            };

            var json = JsonConvert.SerializeObject(requestObject);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            var response = await client.PostAsync(ApiEndpoint, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            
            return ParseResponseContent(responseContent);
        }
    }

    private string ParseResponseContent(string responseContent)
    {
        var lines = responseContent.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.RemoveEmptyEntries);
        var resultText = new StringBuilder();
        
        foreach (var line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            
            try
            {
                var jsonObject = JObject.Parse(line);
                if (jsonObject.TryGetValue("answer", out JToken responseValue))
                {
                    resultText.Append(responseValue.ToString());
                }
            }
            catch (JsonException ex)
            {
                Debug.LogError($"Failed to parse JSON: {ex.Message}");
            }
        }
        
        return resultText.ToString();
    }

    private void AppendTextPrefab(GameObject prefab, string say)
    {
        var newObject = Instantiate(prefab, npcTextParent.transform);
        newObject.GetComponent<TextMeshProUGUI>().text = say;
        Canvas.ForceUpdateCanvases();
        dialogueRect.verticalNormalizedPosition = 0f;
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.LeftControl))
        {
            whisperObject.StartRecording();
        }
        else if (Input.GetKeyUp(KeyCode.LeftControl))
        {
            ProcessVoiceInput();
        }
    }

    private async void ProcessVoiceInput()
    {
        bool success = whisperObject.StopRecording();
        if (success)
        {
            string result = await whisperObject.RunWhisperAsync();
            inputField.text = result;
            await SendQueryAsync();
        }
    }
}