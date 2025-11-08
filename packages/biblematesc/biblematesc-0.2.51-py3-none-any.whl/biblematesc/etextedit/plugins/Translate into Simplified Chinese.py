def translate_into_simplified_chinese(event=None):
    custom_prompt = "请将以下内容翻译成简体中文。如果内容包含程式码，请保持程式码不变，只翻译文字部分。请确保翻译准确且自然流畅。"

    if custom_prompt is not None:
        buffer = event.app.current_buffer if event is not None else text_field.buffer
        selectedText = buffer.copy_selection().text
        content = selectedText if selectedText else buffer.text
        content = agentmake(get_augment_instruction(custom_prompt, content), system="auto" if ApplicationState.auto_agent else None, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
        # insert the improved prompt as a code block
        buffer.insert_text(format_assistant_content(content))
        # Repaint the application; get_app().invalidate() does not work here
        get_app().reset()