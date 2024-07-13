from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
import tiktoken
from retry import retry
import os

from core.config import settings
from utils import log

log = log.Logger(__name__, clevel=log.logging.DEBUG)
UPLOAD_DIR = './uploads'

class Assistant:
    '''
    wrapper openai api
    '''
    supported_models = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo-1106",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "dall-e-3"
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = OpenAI(api_key=settings.openai_key)
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
    
    def file_upload(self, file_name: str, purpose: str="assistants"):
        """
        upload a file
        purpose: ['fine-tune', 'assistants', 'batch',
                'user_data', 'responses', 'vision']
        """
        file_path = os.path.join(UPLOAD_DIR, file_name)
        newfile = self.client.files.create(
            file=open(file_path, "rb"),
            purpose=purpose)
        return newfile
    
    def file_delete(self, file_id: str):
        self.client.files.delete(file_id)

    def create_vs_with_files(self, vector_store_name: str="", files_name: list=[]) -> str:
        """
        upload a list of files to openai vector stores
        """
        try:
            vector_store = self.client.beta.vector_stores.create(name=vector_store_name)
            file_streams = [open(os.path.join(UPLOAD_DIR, path), "rb") for path in files_name]
            file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
        except Exception as err:
            log.debug(f"upload_files error: {err}")
            return None
        return vector_store.id

    def vector_store_files(self, vs_id: str) -> list:
        """
        List vector store files
        """
        res = []
        try:
            vs_files = self.client.beta.vector_stores.files.list(
                vector_store_id=vs_id
            )
            if vs_files is None:
                return []
            for x in vs_files.data:
                res.append({"id": x.id, "created_at": x.created_at})
        except Exception as err:
            log.debug(f"vector_store_files error: {err}")
        return res

    def vs_delete(self, vector_store_id: str):
        """
        delete vector store
        """
        deleted_vector_store = self.client.beta.vector_stores.delete(
            vector_store_id=vector_store_id)
        return deleted_vector_store.deleted

    def vs_upload_file(self, vector_store_id: str, file_name: str):
        """
        Create a vector store file by attaching a File to a vector store.
        upload a file and then create in vector store
        """
        newfile = self.file_upload(file_name)
        vector_store_file = self.client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=newfile.id)
        return vector_store_file

    def vs_delete_file(self, vector_store_id: str, fild_id: str):
        """
        delete a file from vector store
        """
        deleted_vs_file = self.client.beta.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=fild_id
        )

    def create_assistant(self,
            name="assistant",
            description="",
            instructions="you are a helpful assistant",
            model="gpt-4o",
            tools: list=[],
            tool_resources: list=None,
            temperature=1.0):
        """
        creat an assistant
        """
        assistant = self.client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model,
            tools=tools,
            tool_resources=tool_resources,
            temperature=temperature
        )
        return assistant
    
    def update_assistant(self, assistant_id, **kwargs):
        print("uuuuupdate: ", kwargs)
        my_updated_assistant = self.client.beta.assistants.update(
            assistant_id,
            **kwargs
        )

    def delete_assistant(self, assistant_id: str):
        res = self.client.beta.assistants.delete(assistant_id)
        return res

    def create_thread(self) -> str:
        thread = self.client.beta.threads.create()
        return thread.id

    def delete_thread(self, thread_id: str) -> str:
        del_status = self.client.beta.threads.delete(thread_id)
        return del_status.deleted

    def add_thread_message(self,
            thread_id: str,
            role: str,
            message: str|list,
            attachments: list=None):
        """
        create a message
        """
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=message,
            attachments=attachments,
            )
    
    def runs(self, assistant_id: str, thread_id: str, instructions: str=None):
        """
        run a thread.
        instructions paramater will update assistant instructions
        """
        print("this is msg run")
        parms = {}
        if instructions:
            params["instructions"] = instructions
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            **parms,
        ) as stream:
            for text in stream.text_deltas:
                yield text
            # stream.until_done()

    def send_msg_and_run(self,
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
