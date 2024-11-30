from fastcrud import FastCRUD

from ..models.conversation import Conversation
from ..schemas.conversation import ConversationCreateInternal, ConversationDelete

CRUDConversation = FastCRUD[Conversation, ConversationCreateInternal, None, None, ConversationDelete]
crud_conversations = CRUDConversation(Conversation)
