from typing_extensions import override
from openai import AsyncOpenAI, AssistantEventHandler
import tiktoken
from retry import retry
import os

from core.config import settings
from .credit import Credit
from utils import log

log = log.Logger(__name__, clevel=log.logging.DEBUG)
UPLOAD_DIR = './uploads'

class Assistant:
    '''
    wrapper openai api
    '''
    supported_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo-1106",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "dall-e-3"
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = AsyncOpenAI(api_key=settings.openai_key)
        self.credit = Credit()
        print("assistant init: ", self.model)

    def get_messages(self, thread_id: str="") -> list:
        """
        get all messages under a thread
        """
        if thread_id != "":
            thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content[0].text.value,
                }
                for msg in thread_messages.data
            ]
            return messages
        else:
            return []
    
    async def file_upload(self, file_name: str, purpose: str="assistants"):
        """
        upload a file
        purpose: ['fine-tune', 'assistants', 'batch',
                'user_data', 'responses', 'vision']
        """
        file_path = os.path.join(UPLOAD_DIR, file_name)
        newfile = await self.client.files.create(
            file=open(file_path, "rb"),
            purpose=purpose)
        return newfile
    
    async def file_delete(self, file_id: str):
        await self.client.files.delete(file_id)

    async def file_download(self, file_id: str, file_name: str):
        try:
            print("file_download")
            file_data = await self.client.files.content(file_id)
            file_data_bytes = file_data.read()
            with open(os.path.join(UPLOAD_DIR, file_name), "wb") as file:
                file.write(file_data_bytes)
        except Exception as err:
            log.debug(f"file_download error: {err}")
            return err.body

    async def create_vs_with_files(self, vector_store_name: str="", files_name: list=[]) -> str:
        """
        upload a list of files to openai vector stores
        """
        try:
            vector_store = await self.client.beta.vector_stores.create(name=vector_store_name)
            file_streams = [open(os.path.join(UPLOAD_DIR, path), "rb") for path in files_name]
            file_batch = await self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
        except Exception as err:
            log.debug(f"upload_files error: {err}")
            return None
        return vector_store.id

    async def vector_store_files(self, vs_id: str) -> list:
        """
        List vector store files
        """
        res = []
        try:
            vs_files = await self.client.beta.vector_stores.files.list(
                vector_store_id=vs_id
            )
            if vs_files is None:
                return []
            for x in vs_files.data:
                res.append({"id": x.id, "created_at": x.created_at})
        except Exception as err:
            log.debug(f"vector_store_files error: {err}")
        return res

    async def vs_delete(self, vector_store_id: str):
        """
        delete vector store
        """
        deleted_vector_store = await self.client.beta.vector_stores.delete(
            vector_store_id=vector_store_id)
        return deleted_vector_store.deleted

    async def vs_upload_file(self, vector_store_id: str, file_name: str):
        """
        Create a vector store file by attaching a File to a vector store.
        upload a file and then create in vector store
        """
        newfile = await self.file_upload(file_name)
        vector_store_file = await self.client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=newfile.id)
        return vector_store_file

    async def vs_delete_file(self, vector_store_id: str, fild_id: str):
        """
        delete a file from vector store
        """
        deleted_vs_file = await self.client.beta.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=fild_id
        )

    async def create_assistant(self, **kwargs):
        """
        creat an assistant
        """
        assistant = await self.client.beta.assistants.create(**kwargs)
        return assistant
    
    async def update_assistant(self, assistant_id, **kwargs):
        print("uuuuupdate: ", kwargs)
        my_updated_assistant = await self.client.beta.assistants.update(
            assistant_id,
            **kwargs
        )

    async def delete_assistant(self, assistant_id: str):
        try:
            await self.client.beta.assistants.delete(assistant_id)
        except Exception as err:
            log.error(f"delete_assistant error: {err}")

    async def create_thread(self) -> str:
        thread = await self.client.beta.threads.create()
        return thread.id

    async def retrive_thread(self, thread_id):
        thd = await self.client.beta.threads.retrieve(thread_id)
        return thd

    async def delete_thread(self, thread_id: str) -> str:
        del_status = await self.client.beta.threads.delete(thread_id)
        return del_status.deleted

    async def add_thread_message(self,
            thread_id: str,
            role: str,
            message: str|list,
            attachments: list=None):
        """
        create a message
        """
        try:
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=message,
                attachments=attachments,
                )
        except Exception as err:
            log.debug(f"add_thread_message error: {err}")
    
    async def runs(self, user_id: int, assistant_id: str, thread_id: str, message):
        """
        run a thread.
        instructions paramater will update assistant instructions
        """
        print("this is msg run")
        params = {}
        if message.instructions:
            params["instructions"] = message.instructions
        if (message.temperature != None and
            0 <= message.temperature <= 2.0):
            params["temperature"] = message.temperature
        #params["response_format"] = { "type": "json_object" }
        input_tokens = output_tokens = 0
        async with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            **params,
        ) as stream:
            async for event in stream:
                if (event and
                    "thread.run.step" == event.event[:15] and
                    getattr(event.data, 'usage', None)):
                    input_tokens = event.data.usage.prompt_tokens
                    output_tokens = event.data.usage.completion_tokens
                yield event.model_dump_json(exclude_unset=True)
        self.credit.from_tokens(user_id, "gpt-4o", input_tokens, output_tokens)

    async def send_msg_and_run(self,
            assistant_id,
            thread_id,
            instructions,
            message,
            attachments):
        """
        add message to thread and run thread
        """
        self.add_thread_message(assistant_id, thread_id, message, attachments)
        self.run(assistant_id, thread_id, instructions)


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))
