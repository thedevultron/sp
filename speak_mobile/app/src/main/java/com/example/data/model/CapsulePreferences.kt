package com.example.data.model

enum class QuickActionType(val id: String, val label: String, val voiceTrigger: String, val description: String, val promptInstruction: String) {
    REFINE(
        "refine",
        "Refine",
        "refine",
        "Fixes self-corrections ('9pm actually 5pm' -> '5:00 PM'), removes fillers ('um/uh/like'), and normalizes punctuation.",
        "You are an expert voice-to-text refinement engine. Fix user transcript self-corrections (e.g., if user says 'at 9pm actually 5pm' output 'at 5:00 PM'), remove conversational filler words ('um', 'uh', 'like', 'you know'), normalize timestamps, and fix grammar while preserving authentic voice. Output ONLY the refined text:"
    ),
    POLISH_REFINE(
        "polish",
        "Polish",
        "polish",
        "Publication-ready copyedit. Sharpens word choice, flow, and sentence rhythm.",
        "Polish the following text into publication-ready quality. Enhance sentence flow, clarity, and precision while preserving the core message. Output ONLY the polished text:"
    ),
    ELABORATE(
        "elaborate",
        "Elaborate",
        "elaborate",
        "Expands concise thoughts into comprehensive, structured explanations with rich detail.",
        "Elaborate on the following text. Expand the core ideas with thoughtful structure, comprehensive detail, and illustrative clarity. Output ONLY the elaborated text:"
    ),
    MAKE_FORMAL(
        "formal",
        "Formalize",
        "formal",
        "Elevates language to executive, publication-ready professional standards.",
        "Rewrite the following text in an elegant, executive, professional tone suitable for high-stakes business communication. Output ONLY the revised text:"
    ),
    SUMMARIZE(
        "summarize",
        "Summarize",
        "summarize",
        "Distills long speech into crisp, high-signal bullet points.",
        "Summarize the following text into 2-3 crisp, high-signal bullet points. Output ONLY the summary:"
    )
}

data class CustomRefineAction(
    val id: String,
    val name: String,
    val voiceTrigger: String,
    val prompt: String,
    val enabled: Boolean = true
)

data class LexiconEntry(
    val word: String,
    val pronunciationOrContext: String = ""
)

data class CapsulePreferences(
    val themeMode: String = "DARK_OBSIDIAN",
    val blurRadiusDp: Float = 24f,
    val borderOpacity: Float = 0.18f,
    val farRightAction: QuickActionType = QuickActionType.REFINE,
    val userName: String = "User",
    val customLexicon: List<String> = listOf("Speak", "Gemini 3.1 Flash Live", "Kotlin", "Void Violet", "PCM 16kHz"),
    val customSystemPrompt: String = "You are Speak Voice Intelligence, a high-fidelity voice companion and dictation assistant. Transcribe and refine text with pristine accuracy.",
    val proAccessActive: Boolean = true,
    val customApiKey: String = "",
    val backupApiKeys: List<String> = emptyList(),
    val onboardingCompleted: Boolean = true,
    val alwaysOnSmartMode: Boolean = true,
    val hapticFeedbackEnabled: Boolean = true,
    val temperature: Float = 0.3f,
    val maxStoredSessions: Int = 5,
    val verificationActive: Boolean = true, // Verification Active vs Auto-Send
    val drawOverOtherAppsEnabled: Boolean = false, // System Alert Window overlay over all apps
    val autoOpenOnTypingEnabled: Boolean = false, // Auto-summon capsule when typing anywhere
    val autoInsertTextEnabled: Boolean = true, // Auto-insert dictation into focused text field
    val screenShareVisionActive: Boolean = false,
    val screenShareFps: Int = 2,
    val screenShareQuality: String = "720p",
    val screenSharePrivacyMask: Boolean = true,
    val customSignatureMark: String = "",
    val customActions: List<CustomRefineAction> = listOf(
        CustomRefineAction(
            id = "custom_1",
            name = "Bulletize",
            voiceTrigger = "bulletize",
            prompt = "Format the text into clean, structured Markdown bullet points with bold lead-ins. Output only the bullets:",
            enabled = true
        ),
        CustomRefineAction(
            id = "custom_2",
            name = "Action Items",
            voiceTrigger = "tasks",
            prompt = "Extract clear, actionable to-do items from the text, formatted as a checkbox list with owners if mentioned. Output only the checklist:",
            enabled = false
        ),
        CustomRefineAction(
            id = "custom_3",
            name = "Executive Brief",
            voiceTrigger = "executive",
            prompt = "Convert this text into an executive summary paragraph followed by 3 strategic takeaways. Output only the brief:",
            enabled = false
        )
    ),
    val springStiffness: Float = 380f,
    val springDamping: Float = 0.72f
)
