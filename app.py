import streamlit as st
import whisper
import tempfile
import os
from deep_translator import GoogleTranslator
from gtts import gTTS

st.set_page_config(
    page_title="AI Voice Translator",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AI Voice Translator")
st.write("Speak or upload audio and translate it into another language.")

st.divider()

# Load translation languages dynamically
try:
    languages = GoogleTranslator().get_supported_languages(as_dict=True)
except Exception:
    languages = {
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Kannada": "kn",
        "Telugu": "te",
        "Malayalam": "ml",
        "Korean": "ko",
        "Japanese": "ja",
        "Chinese": "zh-CN",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Arabic": "ar",
        "Bengali": "bn",
        "Marathi": "mr",
        "Gujarati": "gu",
        "Punjabi": "pa",
        "Urdu": "ur"
    }

# Create reverse dictionary for language names
language_codes = {
    name.lower(): code
    for name, code in languages.items()
}

st.subheader("🎤 Choose Voice Input")

input_method = st.radio(
    "Select how you want to provide your voice:",
    ["🎙️ Record Voice", "📁 Upload Audio"]
)

audio_data = None
file_name = None

# --------------------------------------------------
# RECORD VOICE
# --------------------------------------------------

if input_method == "🎙️ Record Voice":

    st.write("Click the microphone button and record your voice.")

    audio_data = st.audio_input(
        "🎙️ Record your voice"
    )

    if audio_data is not None:

        st.success("Voice recorded successfully!")

        st.audio(audio_data)

        file_name = "recorded_audio.wav"


# --------------------------------------------------
# UPLOAD AUDIO
# --------------------------------------------------

else:

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["mp3", "wav", "m4a", "ogg", "webm"]
    )

    if uploaded_file is not None:

        audio_data = uploaded_file

        file_name = uploaded_file.name

        st.success("Audio uploaded successfully!")

        st.audio(uploaded_file)

        st.write("File name:", uploaded_file.name)


# --------------------------------------------------
# OUTPUT LANGUAGE
# --------------------------------------------------

st.divider()

st.subheader("🌐 Translation Language")

language_list = sorted(languages.keys())

selected_language = st.selectbox(
    "Choose the language you want to translate into:",
    language_list
)

target_language = languages[selected_language]


# --------------------------------------------------
# PROCESS AUDIO
# --------------------------------------------------

if audio_data is not None:

    st.divider()

    if st.button("🎤 Convert, Translate & Generate Audio"):

        temp_path = None

        try:

            # ------------------------------------------
            # SAVE AUDIO TEMPORARILY
            # ------------------------------------------

            with st.spinner(
                "Preparing your audio..."
            ):

                suffix = ".wav"

                if file_name:
                    extension = os.path.splitext(file_name)[1]

                    if extension:
                        suffix = extension

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_audio:

                    temp_audio.write(
                        audio_data.getbuffer()
                    )

                    temp_path = temp_audio.name


            # ------------------------------------------
            # WHISPER
            # ------------------------------------------

            with st.spinner(
                "🤖 Detecting language and converting speech to text..."
            ):

                model = whisper.load_model("small")

                result = model.transcribe(
                    temp_path,
                    task="transcribe",
                    fp16=False
                )

                recognized_text = result["text"].strip()

                detected_language = result["language"]


            # ------------------------------------------
            # DETECTED LANGUAGE
            # ------------------------------------------

            st.success("Voice converted successfully!")

            st.subheader("🌍 Detected Input Language")

            detected_language_name = detected_language

            for name, code in languages.items():

                if code == detected_language:

                    detected_language_name = name
                    break

            st.info(
                f"Detected Language: {detected_language_name}"
            )


            # ------------------------------------------
            # ORIGINAL TRANSCRIPTION
            # ------------------------------------------

            st.subheader("📝 Your Speech")

            if recognized_text:

                st.write(recognized_text)

            else:

                st.warning(
                    "No speech could be detected in the audio."
                )


            # ------------------------------------------
            # TRANSLATION
            # ------------------------------------------

            st.subheader("🌐 Translated Text")

            if detected_language == target_language:

                translated_text = recognized_text

            else:

                with st.spinner(
                    f"Translating into {selected_language}..."
                ):

                    translated_text = GoogleTranslator(
                        source=detected_language,
                        target=target_language
                    ).translate(
                        recognized_text
                    )


            st.success("Translation completed!")

            st.write(translated_text)


            # ------------------------------------------
            # TEXT TO SPEECH
            # ------------------------------------------

            st.subheader("🔊 Translated Audio")

            audio_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )

            audio_path = audio_file.name

            audio_file.close()

            try:

                with st.spinner(
                    "🔊 Generating translated audio..."
                ):

                    tts = gTTS(
                        text=translated_text,
                        lang=target_language,
                        slow=False
                    )

                    tts.save(audio_path)


                st.success(
                    "Translated audio generated successfully!"
                )

                st.audio(
                    audio_path,
                    format="audio/mp3"
                )

            except Exception:

                st.warning(
                    "The text was translated successfully, "
                    "but audio generation is not available "
                    "for this language."
                )

            finally:

                if os.path.exists(audio_path):

                    os.remove(audio_path)


        except Exception as e:

            st.error(
                "Something went wrong while processing the audio."
            )

            st.write(
                "Please check your internet connection "
                "and try again."
            )

        finally:

            if temp_path is not None:

                if os.path.exists(temp_path):

                    os.remove(temp_path)


else:

    st.info(
        "Please record your voice or upload an audio file first."
    )