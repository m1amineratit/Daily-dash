from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
import requests
from .models import Task, FocusSession
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY=os.getenv("NEWS_API_KEY")
JINA_KEY=os.getenv("JINA_KEY")
OPENROUTER_KEY=os.getenv("OPENROUTER_KEY")
API_KEY="API_KEY"

def summrize_content(content):
    ai_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers = {
            "Authorization" : f"Bearer {OPENROUTER_KEY}",
            "Content-Type" : "application/json",
        },
        json={
            "model" : "meta-llama/llama-4-maverick:free",
            "messages" : [
                {
                    "role" : "user",
                    "content" : f"Summarize this article: \n\n{content}"
                }
            ],
            "temperature" : 0.2,
            "max_tokens" : 300,
        },
        timeout=60
    )
    if ai_response.status_code != 200:
        print("Failed to parse AI response")
        print(OPENROUTER_KEY)
    try:
        ai_data = ai_response.json()
        return ai_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Failed to parse AI response")
        print("RAW:", ai_response.text)
        return None

@login_required
def dashboard(request):
    # --- Fetch top 3 tech news ---
    api_key = "d9c559be99ba4e969eee7f83505affad"
    news_url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={api_key}"

    try:
        news_response = requests.get(news_url, timeout=10)
        news_data = news_response.json()
        top_news = []

        if news_data.get("status") == "ok":
            for article in news_data["articles"][:3]:
                summary = summrize_content(article.get("description", "") or article.get("title", ""))
                if summary:
                    top_news.append({
                        "title": article.get("title"),
                        "link": article.get("url"),
                        "summary" : summary,
                        "source": article.get("source", {}).get("name", "Unknown")
                    })
        else:
            top_news = []
    except Exception as e:
        print("Error fetching NewsAPI data:", e)
        top_news = []

    # --- Fetch Bitcoin price and 24h change ---
    headers = {
        "accept" : "application/json",
        "CB-VERSION" : "2023-10-01",
        "Authorization" : f"Bearer {API_KEY}"
    }
    btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    
    response = requests.get(btc_url, headers=headers)

    btc_data = None
    if response.status_code == 200:
        data = response.json()
        btc_data = {
            "price": data["market_data"]["current_price"]["usd"],
            "change_24h": data["market_data"]["price_change_percentage_24h"],
            "volume_24": data["market_data"]["total_volume"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"]
        }
    else:
        print("Error fetching data:", response.text)
        btc_data = None

        
    # --- Fetch last 3 tasks ---
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')[:3]

    context = {
        'news': top_news,
        'tasks': tasks,
        "btc_data" : btc_data
    }

    return render(request, 'pages/dashboard.html', context)


def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    context = {
        'tasks' : tasks,
    }
    return render(request, 'pages/tasks.html', context)

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Create task but don't save to DB yet
            task = form.save(commit=False)
            # Add the current user
            task.user = request.user
            # Now save to DB
            task.save()
            return redirect('dashboard')  # Redirect to dashboard instead of add_task
    else:
        form = TaskForm()
    
    return render(request, 'pages/add_task.html', {'form': form})


@login_required
def update_task(request, task_id):
    tasks = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=tasks)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = TaskForm(instance=tasks)
    
    return render(request, 'pages/update_task.html', {
        'form': form,
        'tasks': tasks
    })


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')  
    
    return render(request, 'pages/delete_task_confirm.html', {'task': task})

@login_required
def save_session(request):
    if request.method == 'POST':
        FocusSession.objects.create(completed=True)
        return JsonResponse({'status' : 'success'})
