import json
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render
from .forms import ChatForm
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=settings.API_KEY)

# Load package data and calculate last updated date
def load_packages_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'converted_data.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        packages = json.load(file)

    last_updated = (datetime.today() - timedelta(days=13)).strftime("%d %b %Y")
    return packages, last_updated

def generate_response_with_gemini(query, packages_data, last_updated, history):
    # Handle hardcoded identity/introduction queries
    query_lower = query.lower()
    identity_questions = [
        "who are you", "what is your name", "who created you", "who made you", 
        "who developed you", "what is zaib", "who is zaib"
    ]
    if any(phrase in query_lower for phrase in identity_questions):
        return "I am ZAIB (Zong AI Bot), and I was created by Ossama Khan from Marketing, Central-B."

    # Avoid greeting in every response
    first_time = not history
    prompt_intro = ""

    if first_time:
        prompt_intro = "Hi! 😊 Looking for Zong packages? I’m here to help you find the best options.\n\n"

    # Plain package heading
    prompt_intro += f"Zong Packages (Last Updated: {last_updated})\n\n"

    seen_packages = set()
    formatted_packages = []

    for pkg in packages_data:
        name = str(pkg.get('Package Name', '')).strip()
        if not name or name in seen_packages:
            continue
        seen_packages.add(name)

        parts = []
        data = str(pkg.get('Data (GB)', '')).strip()
        onnet = str(pkg.get('On-Net (Zong Mins)', '')).strip()
        offnet = str(pkg.get('Off-Net Mins', '')).strip()
        sms = str(pkg.get('SMS', '')).strip()
        price = str(pkg.get('Price (PKR)', '')).strip()
        validity = str(pkg.get('Validity (Days)', '')).strip()
        cta = str(pkg.get('CTA', '')).strip()

        if data and data.upper() != 'N/A':
            parts.append(f"{data} data")
        if onnet and onnet.upper() != 'N/A':
            parts.append(f"{onnet} on-net mins")
        if offnet and offnet.upper() != 'N/A':
            parts.append(f"{offnet} off-net mins")
        if sms and sms.upper() != 'N/A':
            parts.append(f"{sms} SMS")
        if price and price.upper() != 'N/A' and price.strip() != "":
            parts.append(f"PKR {price}")
        if validity and validity.upper() != 'N/A':
            parts.append(f"valid for {validity} days")
        if cta and cta.upper() != 'N/A':
            parts.append(f"{cta} CTA")

        if parts:
            formatted_packages.append(f"- {name}: {', '.join(parts)}")

    prompt = prompt_intro + "\n".join(formatted_packages)

    if history:
        prompt += "\n\nEarlier messages from the user:\n"
        for h in history[-3:]:
            user_q = h.get('query', '').strip()
            if user_q:
                prompt += f"- {user_q}\n"

    prompt += f"\nUser's latest question:\n- {query}\n\nPlease reply clearly and do not use any formatting like asterisks or Markdown."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()

        return text

    except Exception as e:
        return f"Sorry, there was an error with the Gemini API: {str(e)}"




# Django view to handle chatbot
def chat_view(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    response = ''
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        packages_data, last_updated = load_packages_data()
        chat_history = request.session['chat_history']

        response = generate_response_with_gemini(query, packages_data, last_updated, chat_history)

        chat_history.append({
            'query': query,
            'response': response
        })
        request.session.modified = True

    return render(request, 'chat.html', {
        'response': response,
        'form': ChatForm(),
        'chat_history': request.session.get('chat_history', [])
    })
