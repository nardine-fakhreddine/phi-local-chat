"""Gradio chatbot that talks to a local OpenAI-compatible server (Ollama)."""

import gradio as gr
import openai

# Point the OpenAI client at Ollama's local chat-completions endpoint.
# api_key is required by the SDK but ignored by Ollama.
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="nokeyneeded",
)


def chat_with_openai(message, history):
    """Send the latest user message plus chat history to the model.

    Gradio Chatbot (type="messages") stores history as a list of
    {"role": ..., "content": ...} dicts. Returns the updated history
    and an empty string so the input box is cleared.
    """
    history = history or []

    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    conversation.extend(history)
    conversation.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        # Paid OpenAI models (need a real API key): "gpt-3.5-turbo", "gpt-4o"
        model="phi:latest",
        temperature=0.3,
        messages=conversation,
    )

    # SDK v1+ returns a ChatCompletionMessage object; use .content, not ["content"].
    assistant_reply = response.choices[0].message.content or ""

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": assistant_reply},
    ]

    return history, ""


def gradio_chat_app():
    """Build the Gradio Blocks UI: chat window, input, send, and clear."""
    with gr.Blocks() as app:
        gr.Markdown("## Chat with OpenAI API")
        gr.Markdown("This is a simple chatbot interface using Gradio and OpenAI API.")

        # type="messages" is required by current Gradio (not the old tuple format).
        chatbot = gr.Chatbot(label="Chatbot", type="messages")
        user_input = gr.Textbox(
            label="Your Message",
            placeholder="Type your message here...",
        )
        submit_button = gr.Button("Send")
        clear_button = gr.Button("Clear Chat")

        def clear_chat():
            """Reset the transcript and the input box."""
            return [], ""

        submit_button.click(
            fn=chat_with_openai,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input],
        )
        clear_button.click(
            fn=clear_chat,
            inputs=[],
            outputs=[chatbot, user_input],
        )

    return app


if __name__ == "__main__":
    app = gradio_chat_app()
    app.launch()
