import requests
import json
import urllib.parse
import re
import uuid
import base64

server_url = 'https://voip-middlware.superu.ai'
# server_url = 'http://localhost:5000'

class CallWrapper:
    def __init__(self, api_key):
        self.api_key = api_key

        
    def create(self, from_, to_, first_message_url = None , assistant_id = None , max_duration_seconds = 120 , **kwargs):

        data_json = {
            'from_': from_,
            'to_': to_,
            'assistant_id': assistant_id,
            'max_duration_seconds': max_duration_seconds,
            **kwargs,
            'api_key': self.api_key
        }

        if first_message_url:
            data_json['first_message_url'] = first_message_url

        response = requests.post(
            f'{server_url}/pypi_support/call_create',
            json=data_json,
        )
        return response
        
    
    def analysis(self, call_uuid , custom_fields = None):
        if custom_fields is not None:
            required_keys = {"field", "definition", "outputs_options"}
            for i, field in enumerate(custom_fields):
                if not isinstance(field, dict):
                    raise ValueError(f"custom_fields[{i}] is not a dictionary")
                
                missing_keys = required_keys - field.keys()
                if missing_keys:
                    raise ValueError(f"custom_fields[{i}] is missing keys: {missing_keys}")

                if not isinstance(field["field"], str):
                    raise ValueError(f"custom_fields[{i}]['field'] must be a string")
                if not isinstance(field["definition"], str):
                    raise ValueError(f"custom_fields[{i}]['definition'] must be a string")
                if not isinstance(field["outputs_options"], list) or not all(isinstance(opt, str) for opt in field["outputs_options"]):
                    raise ValueError(f"custom_fields[{i}]['outputs_options'] must be a list of strings")

        response = requests.request(
            "POST",
            f'{server_url}/pypi_support/call_analysis',
            json={'api_key': self.api_key, "call_uuid": call_uuid, "custom_fields": custom_fields}
        )
        return response

    def create_twilio_call(self, phoneNumberId, to_, assistant_id , additional_payload = None):
        request_body = {
            "api_key" : self.api_key,
            "phoneNumberId" : phoneNumberId,
            "to_" : to_,
            "assistant_id" : assistant_id,
            "additional_payload" : additional_payload
        }
        
        # print("twilio call request body" , request_body)
        response = requests.post(f'{server_url}/pypi_support/twilio_call_create', json=request_body)
        # print(response.json())
        return response.json()
    
    def analysis_twilio_call(self, call_uuid , custom_fields = None):
        if custom_fields is not None:
            required_keys = {"field", "definition", "outputs_options"}
            for i, field in enumerate(custom_fields):
                if not isinstance(field, dict):
                    raise ValueError(f"custom_fields[{i}] is not a dictionary")
                
                missing_keys = required_keys - field.keys()
                if missing_keys:
                    raise ValueError(f"custom_fields[{i}] is missing keys: {missing_keys}")

                if not isinstance(field["field"], str):
                    raise ValueError(f"custom_fields[{i}]['field'] must be a string")
                if not isinstance(field["definition"], str):
                    raise ValueError(f"custom_fields[{i}]['definition'] must be a string")
                if not isinstance(field["outputs_options"], list) or not all(isinstance(opt, str) for opt in field["outputs_options"]):
                    raise ValueError(f"custom_fields[{i}]['outputs_options'] must be a list of strings")

        response = requests.request(
            "POST",
            f'{server_url}/pypi_support/twilio_call_analysis',
            json={'api_key': self.api_key, "call_uuid": call_uuid, "custom_fields": custom_fields}
        )
        return response.json()


    # def __getattr__(self, name):
    #     # Delegate all other methods/attributes
    #     return getattr(self._real, name)

class AssistantWrapper:
    def __init__(self, api_key):
        self.api_key = api_key

    def create(self, name, transcriber, model, voice , **kwargs):
        for messages in model['messages']:
            messages['content'] = re.sub(r'[\u0000-\u001F\u007F]+', ' ', messages['content'])
        payload = {
            "name": name,
            "transcriber": transcriber,
            "model": model,
            "voice": voice,
            **kwargs
        }

        response = requests.post(f'{server_url}/pypi_support/assistant_create', json={**payload , 'api_key': self.api_key})
        if response.status_code != 200:
            raise Exception(f"Failed to create assistant: {response.status_code}, {response.text}")
        return response.json()
    
    def create_basic(self, name, voice_id, first_message , system_prompt):
    
        exmaple_json = {
            "name": name,
            "voice": {
                "model": "eleven_flash_v2_5",
                "voiceId": voice_id,
                "provider": "11labs",
                "stability": 0.9,
                "similarityBoost": 0.9,
                "useSpeakerBoost": True,
                "inputMinCharacters": 5
            },
            "model": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    }
                ],
                "provider": "openai",
                "temperature": 0
            },
            "firstMessage": first_message,
            "voicemailMessage": "Please call back when you're available.",
            "endCallFunctionEnabled": True,
            "endCallMessage": "Goodbye.Thank you.",
            "transcriber": {
                "model": "nova-2",
                "language": "en",
                "numerals": False,
                "provider": "deepgram",
                "endpointing": 300,
                "confidenceThreshold": 0.4
            },
            "clientMessages": [
                "transcript",
                "hang",
                "function-call",
                "speech-update",
                "metadata",
                "transfer-update",
                "conversation-update",
                "workflow.node.started"
            ],
            "serverMessages": [
                "end-of-call-report",
                "status-update",
                "hang",
                "function-call"
            ],
            "hipaaEnabled": False,
            "backgroundSound": "office",
            "backchannelingEnabled": False,
            "backgroundDenoisingEnabled": True,
            "messagePlan": {
                "idleMessages": [
                    "Are you still there?"
                ],
                "idleMessageMaxSpokenCount": 2,
                "idleTimeoutSeconds": 5
            },
            "startSpeakingPlan": {
                "waitSeconds": 0.4,
                "smartEndpointingEnabled": "livekit",
                "smartEndpointingPlan": {
                    "provider": "vapi"
                }
            },
            "stopSpeakingPlan": {
                "numWords": 2,
                "voiceSeconds": 0.3,
                "backoffSeconds": 1
            }
        }

        return self.create(**exmaple_json)

    def list(self):
        response = requests.post(f'{server_url}/pypi_support/assistant_list', json={'api_key': self.api_key})
        if response.status_code != 200:
            raise Exception(f"Failed to list assistants: {response.status_code}, {response.text}")
        return response.json()
    
    def get(self, assistant_id):
        response = requests.post(f"{server_url}/pypi_support/assistant_get", json={'api_key': self.api_key, "assistant_id": assistant_id})
        if response.status_code != 200:
            raise Exception(f"Failed to get assistant: {response.status_code}, {response.text}")
        return response.json()

class ToolWrapper:
    def __init__(self, api_key):
        self.api_key = api_key

    def create(self, name, description, parameters, tool_url, tool_url_domain,
               request_start=None, request_complete=None,
               request_failed=None, request_response_delayed=None,
               async_=False, timeout_seconds=10, secret=None, headers=None):
        
        tool_url = f"https://toolcaller.superu.ai/{tool_url}"

        #  add a param in url
        tool_url = urllib.parse.urlparse(tool_url)
        tool_url = tool_url.scheme + '://' + tool_url.netloc + tool_url.path + '?' + tool_url.query + '&base_url=' + tool_url_domain

        messages = []
        if request_start:
            messages.append({"type": "request-start", "content": request_start})
        if request_complete:
            messages.append({"type": "request-complete", "content": request_complete})
        if request_failed:
            messages.append({"type": "request-failed", "content": request_failed})
        if request_response_delayed:
            messages.append({
                "type": "request-response-delayed",
                "content": request_response_delayed,
                "timingMilliseconds": 2000
            })

        payload = {
            "api_key": self.api_key,
            "type": "function",
            "function": {
                "name": name,
                "async": False,
                "description": description,
                "parameters": parameters
            },
            "messages": messages,
            "server": {
                "url": tool_url,
                "timeoutSeconds": 120
            },
            "async_": False
            }

        if secret:
            payload["server"]["secret"] = secret
        if headers:
            payload["server"]["headers"] = headers

        response = requests.post(f'{server_url}/pypi_support/tool_create', headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to create assistant: {response.status_code}, {response.text}")
        return response.json()
    
    def list(self):
        response = requests.get(f'{server_url}/pypi_support/tool_list', headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to list tools: {response.status_code}, {response.text}")
        return response.json()
    
    def get(self, tool_id):
        response = requests.get(f'{server_url}/pypi_support/tool_get', headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get tool: {response.status_code}, {response.text}")
        return response.json()

class ContactWrapper:
    def __init__(self, api_key):
        self.api_key = api_key

    def create_audience(self , audience_name: str , audience_description: str , contacts: list[dict]):
        payload = {
            "audience_name": audience_name,
            "audience_description": audience_description,
            "contacts": contacts
        }

        compulsory_fields = ['first_name', 'country_code', 'phone_number']

        for contact in contacts:
            for field in compulsory_fields:
                if field not in contact:
                    raise ValueError(f"Missing compulsory field '{field}' in contact: {contact}")

            if not isinstance(contact.get('phone_number'), str):
                raise ValueError(f"'phone_number' must be a string in contact: {contact}")
            phone_pattern = re.compile(r'^\d{10,15}$')
            if not phone_pattern.match(contact['phone_number']):
                raise ValueError(f"Invalid 'phone_number' format in contact: {contact}. It should contain only digits and be 10 to 15 digits long.")
            country_code_pattern = re.compile(r'^\+\d{1,4}$')
            if not country_code_pattern.match(contact['country_code']):
                raise ValueError(f"Invalid 'country_code' format in contact: {contact}. It should start with '+' followed by 1 to 4 digits.")

        response = requests.post(f'{server_url}/pypi_support/audience/create', json={**payload , 'api_key': self.api_key})
        if response.status_code != 200:
            raise Exception(f"Failed to create contact: {response.status_code}, {response.text}")
        return response.json()

    def create(self , contact: dict):
        payload = {
            **contact
        }

        compulsory_fields = ['first_name', 'last_name', 'email', 'country_code', 'phone_number']

        
        for field in compulsory_fields:
            if field not in contact:
                raise ValueError(f"Missing compulsory field '{field}' in contact: {contact}")

        if not isinstance(contact.get('phone_number'), str):
            raise ValueError(f"'phone_number' must be a string in contact: {contact}")
        phone_pattern = re.compile(r'^\d{10,15}$')
        if not phone_pattern.match(contact['phone_number']):
            raise ValueError(f"Invalid 'phone_number' format in contact: {contact}. It should contain only digits and be 10 to 15 digits long.")
        country_code_pattern = re.compile(r'^\+\d{1,4}$')
        if not country_code_pattern.match(contact['country_code']):
            raise ValueError(f"Invalid 'country_code' format in contact: {contact}. It should start with '+' followed by 1 to 4 digits.")
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(contact['email']):
            raise ValueError(f"Invalid 'email' format in contact: {contact}. It should be a valid email address.")

        response = requests.post(f'{server_url}/pypi_support/contact/create', json={**payload , 'api_key': self.api_key})
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"Failed to create contact: {response.status_code}, {response.text}")
        return response.json()
    
    def list(self , page : int = 1 , page_size : int = 10):
        response = requests.post(f'{server_url}/pypi_support/contact/list', json={'api_key': self.api_key, 'page': page, 'page_size': page_size})
        if response.status_code != 200:
            raise Exception(f"Failed to list contacts: {response.status_code}, {response.text}")
        return response.json()
    
class PlutoWrapper:
    def __init__(self, api_key , user_id , assistants):
        self.api_key = api_key
        self.user_id = user_id
        self.assistants = assistants
        self.pluto_url = "pluto-ws.superu.ai"
        self.pluto_1_1_url = "pluto-ws.superu.ai"

    def register_call(self, call_uuid , assistant_id , Telephony):
        response = requests.post(f'http://{self.pluto_1_1_url}/register_call', json={'api_key': self.api_key, "call_uuid": call_uuid , "assistant_id": assistant_id , "Telephony": Telephony})
        if response.status_code != 200:
            raise Exception(f"Failed to register call: {response.status_code}, {response.text}")
        return True

    def join_agent_advance(self , pluto_url , call_id , json_for_url):
        response = requests.post(f"http://{pluto_url}/join_agent_advance/{call_id}", 
        json={
            "api_key" : self.api_key,
            "base64_json_data" : json_for_url
        })
        if response.status_code != 200:
            raise Exception(f"Failed to join agent advance: {response.status_code}, {response.text}")
        return response.text

    def create_call(self , voice_id , call_uuid=None , model=None , assistant_id=None , system_prompt=None , first_message=None , language_clue="en-US" , background_audio=False, prewarm_agent=False , localhost=None , Telephony=False , custom_analysis_prompt=None , custom_summary_prompt=None):
        if not call_uuid:
            call_uuid = uuid.uuid4()
            streamId = call_uuid.hex
        call_id = str(call_uuid)
        streamId = call_id.replace("-" , "")
        self.register_call(call_id , assistant_id , Telephony)
        if model == "pluto_1.1":
            if localhost:
                self.pluto_url = f"localhost:{localhost}"
            else:
                self.pluto_url = "pluto-ws.superu.ai"
        if not voice_id:
            raise Exception("Voice ID is required")
        if assistant_id:
            assistant = self.assistants.get(assistant_id)
            if assistant:
                system_prompt = assistant['model']['messages'][0]['content']
                first_message = assistant['firstMessage']
                
                final_system_prompt = system_prompt

                json_for_url = {
                    "eleven_labs_voice_id" : voice_id,
                    "system_message" : final_system_prompt,
                    "first_message" : first_message,
                    "user_id" : self.user_id,
                    "language_clue" : language_clue,
                    "background_audio" : background_audio,
                    "telephony" : Telephony,
                    "custom_analysis_prompt" : custom_analysis_prompt,
                    "custom_summary_prompt" : custom_summary_prompt
                }

                json_for_url = base64.b64encode(json.dumps(json_for_url).encode()).decode()
                json_for_url = json_for_url.replace("+" , "-").replace("/" , "_")

                ws_url = f"ws://{self.pluto_url}/connect_call/{call_id}/{json_for_url}"

                if prewarm_agent:
                    scale_up_url = self.join_agent_advance(self.pluto_url , call_id , json_for_url)
                    ws_url = ws_url.replace(f"/{json_for_url}" , "")
                    if not localhost:
                        ws_url = ws_url.replace("pluto-ws.superu.ai" , scale_up_url)

                return {
                    "streamId" : streamId,
                    "ws_url" : ws_url,
                    "call_id" : call_id
                }
            else:
                raise Exception("Assistant not found")
        
        elif system_prompt and first_message:
            final_system_prompt = system_prompt

            json_for_url = {
                "eleven_labs_voice_id" : voice_id,
                "system_message" : final_system_prompt,
                "first_message" : first_message,
                "user_id" : self.user_id,
                "language_clue" : language_clue,
                "background_audio" : background_audio,
                "telephony" : Telephony,
                "custom_analysis_prompt" : custom_analysis_prompt,
                "custom_summary_prompt" : custom_summary_prompt
            }

            json_for_url = base64.b64encode(json.dumps(json_for_url).encode()).decode()
            json_for_url = json_for_url.replace("+" , "-").replace("/" , "_")

            ws_url = f"ws://{self.pluto_url}/connect_call/{call_id}/{json_for_url}"

            if prewarm_agent:
                scale_up_url = self.join_agent_advance(self.pluto_url , call_id , json_for_url)
                ws_url = ws_url.replace(f"/{json_for_url}" , "")
                if not localhost:
                    ws_url = ws_url.replace("pluto-ws.superu.ai" , scale_up_url)

            return {
                "streamId" : streamId,
                "ws_url" : ws_url,
                "call_id" : call_id
            }
        
        else:
            raise Exception("Assistant ID or System Prompt and First Message is required")
    
    def create_call_plivo(self , voice_id , from_ , to_ , model=None , assistant_id=None , system_prompt=None , first_message=None , language_clue="en-US" , background_audio=False, prewarm_agent=False , localhost=None ,max_duration_seconds=120 , custom_analysis_prompt=None , custom_summary_prompt=None , **kwargs):
        data_json = {
            'from_': from_,
            'to_': to_,
            'max_duration_seconds': max_duration_seconds,
            **kwargs,
            'api_key': self.api_key
        }

        response = requests.post(
            f'{server_url}/pypi_support/pluto/call_create',
            json=data_json,
        )
        
        plivo_call = response.json()

        plivo_call_uuid = plivo_call['call_uuid']

        call_create = self.create_call(voice_id , model=model , call_uuid=plivo_call_uuid , assistant_id=assistant_id , system_prompt=system_prompt , first_message=first_message , language_clue=language_clue , background_audio=background_audio , prewarm_agent=prewarm_agent , localhost=localhost , Telephony=True , custom_analysis_prompt=custom_analysis_prompt , custom_summary_prompt=custom_summary_prompt)

        return plivo_call , call_create

    def get_call(self , call_id , model=None):
        if model == "pluto_1.1":
            self.pluto_url = "pluto-ws.superu.ai"
            
        response = requests.get(f'http://{self.pluto_url}/call_logs/{call_id}', json={'api_key': self.api_key})
        if response.status_code != 200:
            raise Exception(f"Failed to get call: {response.status_code}, {response.text}")
        return response.json()

class SuperU:
    def __init__(self, api_key):
        API_key_validation = self.validate_api_key(api_key)
        self.api_key = api_key
        self.user_id = API_key_validation['user_id']
        self.calls = CallWrapper(self.api_key)
        self.assistants = AssistantWrapper(self.api_key)
        self.tools = ToolWrapper(self.api_key)
        self.pluto = PlutoWrapper(self.api_key , self.user_id , assistants=self.assistants)
        self.contacts = ContactWrapper(self.api_key)

    def validate_api_key(self, api_key):
        response = requests.post(
            # 'https://shared-service.superu.ai/api_key_check',
            f'{server_url}/user/validate-api-key',
            headers={'Content-Type': 'application/json'},
            json={'api_key': api_key}
        )
        if response.status_code != 200:
            raise Exception(f"Invalid API key: {response.status_code}, {response.text}")
        return response.json()
    
    # def __getattr__(self, name):
    #     return getattr(self._client, name)
