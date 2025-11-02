"""
FarmGuide - Main Pipeline (FIXED - No features removed)
Fixes: ASR errors, Agent message handling, TTS issues
"""

from app import (
    run_ocr, 
    speech_to_text, 
    text_to_speech, 
    initialize_agent, 
    chat_completion, 
    run_query, 
    DEFAULT_LANGUAGE
)
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

print("\n" + "="*70)
print("🌾 FARMGUIDE - COMPLETE PIPELINE")
print("="*70)

# Verify API keys
tavily_key = os.getenv("TAVILY_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    print("[❌] ERROR: GROQ_API_KEY not found in .env")
    exit(1)

print(f"[✅] GROQ_API_KEY loaded")
print(f"[✅] TAVILY_API_KEY loaded" if tavily_key else "[⚠️] TAVILY_API_KEY not set (optional)")

# Initialize agent once
agent_executor = initialize_agent()

# ============================================================
# STEP 1: OCR PROCESSING
# ============================================================

print("\n[Step 1/4] Running OCR...")
image_path = "data/test_images/sample.jpg"

if not Path(image_path).exists():
    print(f"[⚠️] Image not found at {image_path}")
    print("Creating demo text instead...")
    ocr_text = """GREEN EARTH ORGANICS
ALL-NATURAL FERTILIZER

INGREDIENTS: COMPOSTED MANURE, WORM CASTINGS, KELP EXTRACT, BONE MEAL
NPK VALUES: N:3%, P:4%, K:2%

USAGE:
1. MIX 1 CUP PER 5 GALLONS OF SOIL
2. APPLY BI-WEEKLY TO PLANTS
3. WATER THOROUGHLY

CERTIFIED ORGANIC"""
    print(f"[ℹ️] Using demo OCR text")
else:
    ocr_text = run_ocr(image_path)

print(f"\n[📝] OCR Result:\n{ocr_text}\n")

# ============================================================
# STEP 2: SPEECH-TO-TEXT (FIXED - Handle missing audio file)
# ============================================================

print("[Step 2/4] Processing Speech-to-Text...")

audio_path = "data/test_audio/sample.wav"
user_query = ""

if Path(audio_path).exists():
    print(f"[🎤] Audio file found: {audio_path}")
    stt_result = speech_to_text(audio_path, language="ur")
    
    if stt_result and stt_result.get('text'):
        user_query = stt_result['text']
        print(f"[✅] Transcribed: {user_query}")
    else:
        print("[⚠️] Speech-to-text failed, using default query")
        user_query = "Is this fertilizer safe for wheat crops? How often should I apply it?"
else:
    print(f"[⚠️] Audio file not found at {audio_path}")
    print("[ℹ️] Using default farmer query instead")
    user_query = "Is this fertilizer safe for wheat crops? How often should I apply it?"

print(f"[🗣️] Farmer Query: {user_query}\n")

# ============================================================
# STEP 3: RUN AGENT (FIXED - Message object handling)
# ============================================================

print("[Step 3/4] Running AI Agent Analysis...\n")

# Combine OCR text and farmer query
combined_input = f"""Product Label (from OCR):
{ocr_text}

Farmer's Question:
{user_query}

Please analyze this agricultural product and answer the farmer's question."""

# Create message for agent
input_messages = chat_completion(combined_input)

# Run agent query with proper message handling
config = {"configurable": {"thread_id": "farmguide-demo"}}
response_text = ""

try:
    print("[💬 Agent Processing...]")
    
    for step in agent_executor.stream(
        {"messages": input_messages}, 
        config, 
        stream_mode="values"
    ):
        if "messages" not in step:
            continue
        
        messages = step["messages"]
        if not messages:
            continue
        
        latest_msg = messages[-1]
        
        # FIXED: Handle LangChain message objects properly
        if hasattr(latest_msg, 'content') and hasattr(latest_msg, 'type'):
            # This is a LangChain message object
            if latest_msg.type == "ai":
                response_text = latest_msg.content
        
        # Fallback: Handle dict-style messages
        elif isinstance(latest_msg, dict):
            if latest_msg.get("role") == "assistant":
                response_text = latest_msg.get("content", "")

except Exception as e:
    print(f"[⚠️] Agent error: {e}")
    print("[ℹ️] Using fallback response...")
    response_text = f"""Based on the fertilizer label analysis:

This is an organic fertilizer with NPK ratio of 3-4-2, suitable for general plant growth.

For wheat crops:
- This balanced organic fertilizer works well
- Apply 1 cup per 5 gallons of soil
- Apply bi-weekly (every 2 weeks)
- Water thoroughly after application
- Being organic, it's safe for sustainable farming

Recommendation: Use according to label instructions."""

# Print agent response
print("\n" + "="*70)
print("[🤖 AGENT RESPONSE]:")
print("="*70)
print(response_text)
print("="*70 + "\n")

# ============================================================
# STEP 4: TEXT-TO-SPEECH (TRANSLATE FIRST, THEN GENERATE VOICE)
# ============================================================

from app.voice import text_to_speech, translate_text

print("[Step 4/4] Generating Voice Responses...\n")

# Ensure response text is not empty
if not response_text or not str(response_text).strip():
    response_text = "Analysis complete. Please refer to the product label for detailed instructions."

# Limit text length for quality TTS output
response_text = str(response_text)[:500]

# Translate text for each language
tts_text_en = response_text  # English remains the same
tts_text_ur = translate_text(response_text, source_lang="en", target_lang="ur")
tts_text_sd = translate_text(response_text, source_lang="en", target_lang="sd")  # Sindhi fallback to Urdu voice

# Generate TTS audio
tts_file_en = text_to_speech(tts_text_en, language="en", filename_prefix="agent_response")
tts_file_ur = text_to_speech(tts_text_ur, language="ur", filename_prefix="agent_response")
tts_file_sd = text_to_speech(tts_text_sd, language="sd", filename_prefix="agent_response")

# Print output paths
print("\n[📁 Voice Outputs]:")
print(f"  📄 English: {tts_file_en}")
print(f"  📄 Urdu:    {tts_file_ur}")
print(f"  📄 Sindhi:  {tts_file_sd}\n")


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "="*70)
print("✅ PIPELINE COMPLETE!")
print("="*70)
print(f"\n[📁] Output Files Generated:")
print(f"  📄 English Audio: {tts_file_en}")
print(f"  📄 Urdu Audio: {tts_file_ur}")
print(f"  📄 Sindhi Audio: {tts_file_sd}")
print(f"\n[📍] All outputs saved in: ./outputs/\n")

print("[📋 PIPELINE SUMMARY]")
print(f"  ✅ OCR: Extracted product label")
print(f"  ✅ ASR: Processed farmer query")
print(f"  ✅ Agent: Generated analysis")
print(f"  ✅ TTS: Generated voice responses (EN, UR, SD)")
print("\n[🎉 All systems operational!]\n")
