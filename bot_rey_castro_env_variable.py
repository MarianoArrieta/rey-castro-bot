
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# Leer credenciales desde variable de entorno
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("cumples_rey_castro").sheet1

app = Flask(__name__)
user_data = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    lower_msg = incoming_msg.lower()
    if from_number not in user_data:
        if lower_msg in ["hola", "buenas", "hey", "menu", "menú"]:
            msg.body(
                "👋 ¡Hola! Bienvenido\n"
                "Soy el asistente virtual de REY 👑 CASTRO\n\n"
                "Por favor seleccioná una opción respondiendo con el número:\n\n"
                "1️⃣ HORARIOS 🕒\n"
                "2️⃣ PROMOS INGRESOS 🎟️\n"
                "3️⃣ MENÚ 📒\n"
                "4️⃣ UBICACIÓN 📍\n"
                "5️⃣ REDES SOCIALES 🧍‍♂️🧍‍♀️\n"
                "6️⃣ CUMPLEAÑOS 🎂\n"
                "7️⃣ SÁBADO 🎤"
            )
        elif lower_msg == "1":
            msg.body("🕒 Nuestro horario es de 01:00 AM hasta 06:00 AM")
        elif lower_msg == "2":
            msg.body(
                "🎟️ *Ingresos y promociones:*\n"
                "👩‍🦰 Damas: $7000 con un trago de regalo\n"
                "🧔 Caballeros: $10.000 con un trago de regalo\n\n"
                "🍾 1 ingreso + botella Federico de Alvear: $17.000\n"
                "🥂 2 ingresos + botella Chandon: $35.000\n"
                "🍹 2 ingresos + botella Smirnoff con jugo: $35.000"
            )
        elif lower_msg == "3":
            msg.body("📒 Mirá nuestra carta de tragos acá:\n👉 https://drive.google.com/file/d/1PmzIrWXkne6FAylnhDAQeJ5ZLUn9mtfP/view?usp=sharing")
        elif lower_msg == "4":
            msg.body("📍 Nuestra ubicación es:\n👉 https://maps.app.goo.gl/GqVhUp1j5fjVBcPRA")
        elif lower_msg == "5":
            msg.body(
                "🗣👥 *NUESTRAS REDES SOCIALES SON:*\n\n"
                "📸 Instagram:\nhttps://instagram.com/reycastro.oficial?utm_medium=copy_link\n\n"
                "🎵 TikTok:\nhttps://www.tiktok.com/@reyclub?_t=8glKz8e6TbC&_r=1\n\n"
                "🔍 Google:\nhttps://www.google.com/search?q=rey+castro"
            )
        elif lower_msg == "6":
            user_data[from_number] = {"step": "name"}
            msg.body("🎂 ¡Vamos a registrar tu cumple!\nPor favor, decime tu *nombre y apellido*.")
        elif lower_msg == "7":
            msg.body("🎤 Este sábado en Rey Castro")
            msg.media("https://drive.google.com/uc?export=view&id=13VW35ik-3YYe8I3rlRWo7hR-OwMYyBPC")
        else:
            msg.body("🙈 No entendí tu mensaje. Escribí 'hola' para ver las opciones del menú.")
    else:
        step = user_data[from_number]["step"]
        if step == "name":
            user_data[from_number]["name"] = incoming_msg
            user_data[from_number]["step"] = "date"
            msg.body("📅 ¿Qué día es tu cumpleaños? (formato DD/MM)")
        elif step == "date":
            user_data[from_number]["date"] = incoming_msg
            user_data[from_number]["step"] = "phone"
            msg.body("📱 ¡Perfecto! Ahora decime tu número de teléfono.")
        elif step == "phone":
            user_data[from_number]["phone"] = incoming_msg
            name = user_data[from_number]["name"]
            date = user_data[from_number]["date"]
            phone = user_data[from_number]["phone"]
            now = datetime.now()
            fecha = now.strftime("%d/%m/%Y")
            hora = now.strftime("%H:%M")
            sheet.append_row([name, date, phone, fecha, hora])
            msg.body("✅ ¡Listo! Tu cumpleaños fue registrado. Nos vemos en Rey Castro 🎉🍾")
            del user_data[from_number]

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
