import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

st.title("Detector de Visuales.")
st.subheader("Vamos a descubrir si eres un VJ.")

# Cambia la ruta de la imagen para asegurarte de que está en la carpeta Traductor
image = Image.open('Traductor/Tranli.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona"   
             " la configuración de lenguaje que necesites.")

st.write("Toca el Botón y habla lo que quieres traducir")

stt_button = Button(label=" Escuchar  🎤", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except FileExistsError:
        pass

    st.title("Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés"),
    )

    lang_dict = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr"
    }
    
    input_language = lang_dict[in_lang]

    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Francés"),
    )
    output_language = lang_dict[out_lang]

    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
            "Francia",
        ),
    )

    tld_dict = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }
    tld = tld_dict[english_accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[:20] if len(text) >= 20 else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(output_text)

    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        if mp3_files:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print(f"Deleted {f}")

    remove_files(7)
