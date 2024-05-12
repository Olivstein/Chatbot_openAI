from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from openai import AzureOpenAI
import json
# from dotenv import load_dotenv
#load_dotenv()
## uvicorn main:app --reload

app = FastAPI()
templates = Jinja2Templates(directory = "templates")

client = AzureOpenAI(
    azure_endpoint = "https://code-doc-gen.openai.azure.com/", 
    api_key = "5301ba53492b46f1959bb93859ccd58e",  
    api_version = "2024-02-15-preview")

chat_responses =[]

@app.get("/", response_class = HTMLResponse)
async def chat_page(request: Request):
  return templates.TemplateResponse("home.html", {"request":request, "chat_responses": chat_responses})

chat_log = [{'role': 'system',
             'content': 'You are a Pyhton tutor AI, compeltely dedicate to teach users how to learn Python from' \
             'scratch. Please provide clear instruccion on Python concepts'}]



@app.websocket("/ws")
async def chat(websocket: WebSocket):

  await websocket.accept()
  while True:
    user_input = await websocket.receive_text()
    chat_log.append({'role':'user','content': user_input})
    chat_responses.append(user_input)

    try:
      response = client.chat.completions.create(
        model="code-doc-gen-gtp4-32k", # model = "deployment_name"
        messages = chat_log, temperature=0.6,
        max_tokens=800, top_p=0.95, frequency_penalty=0, presence_penalty=0,stream=True
        )
      
      ai_response = ''

      for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content is not None:
          ai_response += chunk.choices[0].delta.content
          await websocket.send_text(chunk.choices[0].delta.content)
      chat_responses.append(ai_response)

    except Exception as e:
      await websocket.send_text(f'Error: {str(e)} jeje')
      break



@app.post("/", response_class = HTMLResponse)
async def chat(request: Request ,user_input: Annotated[str, Form()]):

  chat_log.append({'role':'user','content': user_input})
  chat_responses.append(user_input)

  response = client.chat.completions.create(
  model="code-doc-gen-gtp4-32k", # model = "deployment_name"
  messages = chat_log, temperature=0.6,
  max_tokens=800, top_p=0.95, frequency_penalty=0, presence_penalty=0,
  stop=None
    )
  
  bot_response = response.choices[0].message.content
  chat_log.append({'role':'assistant','content':bot_response})
  chat_responses.append(bot_response)

  return templates.TemplateResponse("home.html", {"request":request, "chat_responses": chat_responses})


@app.get("/image", response_class = HTMLResponse)
async def image_page(request: Request):
  return templates.TemplateResponse("image.html",{"request": request})


image_client = AzureOpenAI(
    api_version="2024-02-01",
    azure_endpoint="https://testagents.openai.azure.com/",
    api_key= "599c543588d1494d8ad17be53c6b2049",
)

@app.post("/image", response_class = HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
  
  response = image_client.images.generate(
    model="Dalle3", # the name of your DALL-E 3 deployment
    prompt=user_input,
    n=1,
    size = "1024x1024"
    )
  image_url = json.loads(response.model_dump_json())['data'][0]['url']
  return templates.TemplateResponse("image.html", {"request":request, "image_url": image_url})



# def generate_paragraph(input):

#   client = AzureOpenAI(
#     azure_endpoint = "https://openai-test-cog-services-east-2.openai.azure.com/", 
#     api_key=os.environ["azure_api_key"],  
#     api_version="2024-02-15-preview"
#   )
  
#   message_text = [{"role":"system","content":f"""Hi , you are the expert english content writer, please explain the following data {input} in english paragraph. """
#   }]

#   completion = client.chat.completions.create(
#     model="GPT4CogServices", # model = "deployment_name"
#     messages = message_text,
#     temperature=0.1,
#     max_tokens=1000,
#     top_p=0.95,
#     frequency_penalty=0,
#     presence_penalty=0,
#     stop=None
#   )
#   return completion.choices

# message_text = [{"role":"system",
#                  "content":"You are the CEO of Apple."
#                  },{
#                    'role':'assistant',
#                    'content':'iPhone is awesome?'
#                  },{
#                    'role':'user',
#                    'content':'What year was this released?'
#                  }]




#print(completion)

#  client = AzureOpenAI(
#     azure_endpoint = "https://code-doc-gen.openai.azure.com/", 
#     api_key = "5301ba53492b46f1959bb93859ccd58e",  
#     api_version = "2024-02-15-preview"
#   )

# while True:
#   user_input = input()
#   if user_input.lower() == 'stop':
#     break
#   chat_log.append({'role':'user','content': user_input})
#   response = client.chat.completions.create(
#   model="code-doc-gen-gtp4-32k", # model = "deployment_name"
#   messages = chat_log,
#   temperature=0.6,
#   max_tokens=800,
#   top_p=0.95,
#   frequency_penalty=0,
#   presence_penalty=0,
#   stop=None
#     )
  
#   bot_response = response.choices[0].message.content
#   chat_log.append({'role':'assistant',
#                    'content':bot_response})
#   return bot_response