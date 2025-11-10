"""Main conversation service orchestrating the chatbot flow."""

import json
import logging
from datetime import datetime

from langchain_core.language_models.chat_models import BaseChatModel

from octopus_sensing_sara.core.config import Settings
from octopus_sensing_sara.core.prompt_builder import ConversationalPromptBuilder
from octopus_sensing_sara.models.schemas import ChatRequest, ChatResponse, Message, MessageRole
from octopus_sensing_sara.services.memory_service import MemoryService
from octopus_sensing_sara.services.user_service import UserService

logger = logging.getLogger(__name__)


class ConversationService:
    """Orchestrates conversation flow with memory and user management."""

    def __init__(
        self,
        llm: BaseChatModel,
        memory_service: MemoryService,
        user_service: UserService,
        prompt_builder: ConversationalPromptBuilder,
        summarization_llm: BaseChatModel,
        settings: Settings,
    ):
        """Initialize conversation service.

        Args:
            llm: Main LLM for conversations
            memory_service: Memory management service
            user_service: User profile service
            prompt_builder: Prompt construction service
            summarization_llm: LLM for summarization tasks
            settings: Application settings
        """
        self.llm = llm
        self.memory_service = memory_service
        self.user_service = user_service
        self.prompt_builder = prompt_builder
        self.summarization_llm = summarization_llm
        self.settings = settings

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and generate response.

        This is the main orchestration method that:
        1. Manages session
        2. Gets context (user profile + memory)
        3. Extracts user info from message
        4. Builds prompt
        5. Calls LLM
        6. Saves interaction
        7. Checks if summarization needed

        Args:
            request: Chat request from user

        Returns:
            ChatResponse with assistant's reply

        Example:
            >>> request = ChatRequest(user_id="user_123", message="Hello!")
            >>> response = await service.process_message(request)
        """
        try:
            # ==================== SESSION INITIALIZATION ====================
            session_id = request.session_id or self._generate_session_id(request.user_id)

            logger.info("╔" + "═" * 78 + "╗")
            logger.info("║" + " " * 25 + "NEW INTERACTION" + " " * 38 + "║")
            logger.info("╠" + "═" * 78 + "╣")
            logger.info(f"║ User ID      : {request.user_id:<62} ║")
            logger.info(f"║ Session ID   : {session_id:<62} ║")
            logger.info(f"║ Query        : {request.message[:60]:<62} ║")
            if len(request.message) > 60:
                logger.info(f"║                {request.message[60:120]:<62} ║")
            logger.info("╚" + "═" * 78 + "╝")

            # ==================== STEP 1: LOAD CONTEXT ====================
            logger.info("")
            logger.info("┌─ STEP 1: Loading Conversation Context")
            logger.info("│")

            user_profile, recent_messages = await self.memory_service.get_conversation_context(
                request.user_id, session_id
            )

            logger.info(f"│  → Short-term memory: {len(recent_messages)} messages loaded")

            # Get or create user profile if not exists
            if not user_profile:
                logger.info("│  → User Profile: Creating new profile")
                user_profile = await self.user_service.get_or_create_user_profile(
                    request.user_id
                )
            else:
                logger.info(f"│  → User Profile: Loaded existing profile")
                logger.info(f"│     • Name: {user_profile.name or 'Not set'}")
                logger.info(f"│     • Total messages: {user_profile.total_messages}")
                logger.info(f"│     • Key facts: {len(user_profile.key_facts)}")
                logger.info(f"│     • Session summaries: {len(user_profile.session_summaries)}")
                if user_profile.key_facts:
                    logger.info(f"│     • Recent facts: {', '.join(user_profile.key_facts[-3:])}")

            logger.info("└─ Step 1 complete")

            # ==================== STEP 2: BUILD PROMPT ====================
            logger.info("")
            logger.info("┌─ STEP 2: Building LLM Prompt")
            logger.info("│")

            # Create User Message
            user_message = Message(
                role=MessageRole.USER,
                content=request.message,
                timestamp=datetime.now(),
                metadata=request.metadata,
            )

            # Add user message to recent messages for prompt building
            messages_for_prompt = recent_messages + [user_message]

            conversation_prompt = self.prompt_builder.build_conversation_prompt(
                messages_for_prompt, user_profile
            )

            logger.info(f"│  → Total messages in prompt: {len(conversation_prompt)}")
            logger.info(f"│  → System prompt length: {len(conversation_prompt[0]['content'])} chars")
            logger.info(f"│  → Conversation history: {len(messages_for_prompt)} messages")
            if user_profile.session_summaries:
                logger.info(f"│  → Session summaries included: {len(user_profile.session_summaries)}")
            logger.info("└─ Step 2 complete")

            # ==================== STEP 3: CALL LLM ====================
            logger.info("")
            logger.info("┌─ STEP 3: Calling LLM")
            logger.info("│")
            logger.info(f"│  → Provider: {self.settings.llm_provider}")
            logger.info(f"│  → Model: {self.settings.llm_model}")
            logger.info(f"│  → Temperature: {self.settings.llm_temperature}")
            logger.info(f"│  → Max tokens: {self.settings.llm_max_tokens}")

            import time
            start_time = time.time()
            response = await self.llm.ainvoke(conversation_prompt)
            elapsed_time = time.time() - start_time

            # Extract response text
            assistant_response = response.content

            logger.info(f"│  → Response received in {elapsed_time:.2f}s")
            logger.info(f"│  → Response length: {len(assistant_response)} chars")
            logger.info(f"│  → Preview: {assistant_response[:100]}...")
            logger.info("└─ Step 3 complete")

            # ==================== STEP 4: SAVE INTERACTION ====================
            logger.info("")
            logger.info("┌─ STEP 4: Saving Interaction")
            logger.info("│")

            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=assistant_response,
                timestamp=datetime.now(),
                metadata={},
            )

            await self.memory_service.save_interaction(
                session_id, request.user_id, user_message, assistant_message
            )
            logger.info("│  → Saved to short-term memory (STM)")
            logger.info("│  → Saved to long-term database (LTM)")
            logger.info("│  → User statistics updated")
            logger.info("└─ Step 4 complete")

            # ==================== STEP 5: CHECK SUMMARIZATION ====================
            if user_profile.total_messages >= self.settings.long_term_memory_summary_threshold:
                logger.info("")
                logger.info("┌─ STEP 5: Conversation Summarization")
                logger.info("│")
                logger.info(f"│  → Threshold reached: {user_profile.total_messages} messages")
                logger.info(f"│  → Triggering background summarization...")
                try:
                    await self._summarize_conversation(request.user_id, session_id)
                    logger.info("│  → Summarization completed")
                except Exception as e:
                    logger.error(f"│  → Summarization failed (non-critical): {e}")
                logger.info("└─ Step 5 complete")

            # ==================== INTERACTION COMPLETE ====================
            logger.info("")
            logger.info("╔" + "═" * 78 + "╗")
            logger.info("║" + " " * 25 + "INTERACTION COMPLETE" + " " * 33 + "║")
            logger.info("╠" + "═" * 78 + "╣")
            logger.info(f"║ Response time    : {elapsed_time:.2f}s{' ' * 56} ║")
            logger.info(f"║ Total messages   : {user_profile.total_messages + 2:<60} ║")
            logger.info("╚" + "═" * 78 + "╝")
            logger.info("")

            return ChatResponse(
                session_id=session_id,
                message=assistant_response,
                timestamp=datetime.now(),
                metadata={},
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise

    async def _summarize_conversation(self, user_id: str, session_id: str) -> None:
        """Summarize conversation and update user profile.

        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        try:
            logger.info(f"Starting conversation summarization for user {user_id}")

            # Get all messages from session
            _, messages = await self.memory_service.get_conversation_context(user_id, session_id)

            if not messages:
                logger.warning("No messages found for summarization")
                return

            # Build summarization prompt
            summary_prompt = self.prompt_builder.build_summarization_prompt(messages)

            # Call summarization LLM
            response = await self.summarization_llm.ainvoke([{"role": "user", "content": summary_prompt}])

            # Parse response (expecting JSON format)
            try:
                # Clean up response content - remove markdown code blocks if present
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                if content.startswith("```"):
                    content = content[3:]  # Remove ```
                if content.endswith("```"):
                    content = content[:-3]  # Remove closing ```
                content = content.strip()

                # Parse JSON
                summary_data = json.loads(content)

                # Extract summary
                summary = summary_data.get("summary", "")
                if summary:
                    await self.user_service.update_conversation_summary(user_id, summary)

                # Extract and add key facts
                key_facts = summary_data.get("key_facts", [])
                for fact in key_facts:
                    await self.user_service.add_key_fact(user_id, fact)

                logger.info(
                    f"Summarization complete: summary={bool(summary)}, "
                    f"facts={len(key_facts)}"
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse summarization response: {e}")
                # Try to use the raw text as summary
                await self.user_service.update_conversation_summary(
                    user_id, response.content[:500]
                )

        except Exception as e:
            logger.error(f"Error during summarization: {e}", exc_info=True)
            # Don't raise - summarization is not critical

    async def get_conversation_history(self, session_id: str) -> list[Message]:
        """Get full conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages in the conversation

        Example:
            >>> messages = await service.get_conversation_history("session_123")
        """
        try:
            from octopus_sensing_sara.storage.repositories import ConversationRepository

            # We would need access to the repository here
            # For now, we'll use the memory service
            memory = self.memory_service.get_or_create_memory(session_id)

            # Load from database if empty
            if not memory.chat_memory.messages:
                await self.memory_service.load_memory_from_db(session_id, memory)

            # Convert to Message objects
            messages = []
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

            for msg in memory.chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    role = MessageRole.USER
                elif isinstance(msg, AIMessage):
                    role = MessageRole.ASSISTANT
                elif isinstance(msg, SystemMessage):
                    role = MessageRole.SYSTEM
                else:
                    continue

                messages.append(
                    Message(
                        role=role, content=msg.content, timestamp=datetime.now(), metadata={}
                    )
                )

            return messages

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            raise

    async def summarize_and_close_session(self, user_id: str, session_id: str) -> dict:
        """Summarize a session and save it to user profile.

        Args:
            user_id: User identifier
            session_id: Session identifier to close

        Returns:
            Dictionary with summary info

        Example:
            >>> result = await service.summarize_and_close_session("user_123", "session_456")
        """
        try:
            logger.info("")
            logger.info("╔" + "═" * 78 + "╗")
            logger.info("║" + " " * 27 + "CLOSING SESSION" + " " * 36 + "║")
            logger.info("╠" + "═" * 78 + "╣")
            logger.info(f"║ User ID      : {user_id:<62} ║")
            logger.info(f"║ Session ID   : {session_id:<62} ║")
            logger.info("╚" + "═" * 78 + "╝")

            # Get all messages from the session
            _, messages = await self.memory_service.get_conversation_context(user_id, session_id)

            if not messages or len(messages) == 0:
                logger.warning("│  ✗ No messages found in session, skipping summarization")
                return {"success": False, "message": "No messages to summarize"}

            # Build summarization prompt
            logger.info("")
            logger.info("┌─ Creating Session Summary")
            logger.info("│")
            logger.info(f"│  → Total messages to summarize: {len(messages)}")

            summary_prompt = self.prompt_builder.build_summarization_prompt(messages)

            # Call LLM to generate summary
            logger.info(f"│  → Calling LLM for summarization...")
            response = await self.summarization_llm.ainvoke([{"role": "user", "content": summary_prompt}])

            # Parse response
            summary_text = ""
            extracted_facts = []

            try:
                # Clean up response content - remove markdown code blocks if present
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                if content.startswith("```"):
                    content = content[3:]  # Remove ```
                if content.endswith("```"):
                    content = content[:-3]  # Remove closing ```
                content = content.strip()

                # Parse JSON
                summary_data = json.loads(content)
                summary_text = summary_data.get("summary", "")

                # If summary is empty, try to extract from nested structure
                if not summary_text and isinstance(summary_data.get("summary"), dict):
                    summary_text = json.dumps(summary_data.get("summary"))

                # Extract and add key facts if present
                key_facts = summary_data.get("key_facts", [])
                for fact in key_facts:
                    await self.user_service.add_key_fact(user_id, fact)
                    extracted_facts.append(fact)

            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"│  ⚠ Failed to parse summary JSON: {e}")
                # Use raw response if not JSON (limit to 500 chars)
                summary_text = response.content[:500]

            logger.info(f"│  → Summary generated ({len(summary_text)} chars)")
            logger.info(f"│  → Key facts extracted: {len(extracted_facts)}")
            if extracted_facts:
                for i, fact in enumerate(extracted_facts, 1):
                    logger.info(f"│     {i}. {fact}")

            # Add session summary to user profile
            await self.user_service.add_session_summary(
                user_id=user_id,
                session_id=session_id,
                summary=summary_text,
                message_count=len(messages)
            )

            logger.info("│  → Summary saved to user profile")
            logger.info("└─ Session closed successfully")
            logger.info("")
            logger.info(f"Summary preview: {summary_text[:120]}...")
            logger.info("")

            return {
                "success": True,
                "summary": summary_text,
                "message_count": len(messages),
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"✗ Error summarizing session: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID.

        Args:
            user_id: User identifier

        Returns:
            Generated session ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}_{timestamp}"
