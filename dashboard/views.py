from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
import requests
from .models import Task, FocusSession
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

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
                top_news.append({
                    "title": article.get("title"),
                    "link": article.get("url"),
                    "source": article.get("source", {}).get("name", "Unknown")
                })
        else:
            top_news = []
    except Exception as e:
        print("Error fetching NewsAPI data:", e)
        top_news = []

    # --- Fetch Bitcoin price and 24h change ---
    btc_url = "https://coinmarketcap.com/currencies/bitcoin/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/120.0.0.0 Safari/537.36"
    }
    btc_response = requests.get(btc_url, headers=headers)
    btc_soup = BeautifulSoup(btc_response.text, 'html.parser')
    
    price_span = btc_soup.find('span', class_='sc-65e7f566-0 esyGGG base-text')
    bitcoin_price = price_span.text if price_span else "N/A"

    volum_span = btc_soup.find('div', class_="BasePopover_base__T5yOf")
    if volum_span:
        volum_price = volum_span.find("span").get_text(strip=True)
        
    market_span = btc_soup.find('div', class_='CoinMetrics_overflow-content__tlFu7')
    market_price = market_span.text if market_span else "N/A"

    change_p = btc_soup.find('p', class_='sc-71024e3e-0 sc-9e7b7322-1 bgxfSG dXVXKV change-text')
    bitcoin_change = change_p.text if change_p else "N/A"

    # --- Fetch last 3 tasks ---
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')[:3]

    context = {
        'news': top_news,
        'bitcoin_price': bitcoin_price,
        'bitcoin_change': bitcoin_change,
        'market_price' : market_price,
        'volum_price' : volum_price,
        'tasks': tasks
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

def save_session(request):
    if request.method == 'POST':
        FocusSession.objects.create(completed=True)
        return JsonResponse({'status' : 'success'})

@require_GET
def bitcoin_price_api(request):
    btc_url = "https://coinmarketcap.com/currencies/bitcoin/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/120.0.0.0 Safari/537.36"
    }
    btc_response = requests.get(btc_url, headers=headers)
    btc_soup = BeautifulSoup(btc_response.text, 'html.parser')
    
    # Update these selectors based on the current HTML structure!
    price_span = btc_soup.find('div', class_='priceValue')
    bitcoin_price = price_span.text if price_span else "N/A"

    change_span = btc_soup.find('span', class_='sc-15yy2pl-0 feeyND')
    bitcoin_change = change_span.text if change_span else "N/A"

    market_span = btc_soup.find('div', string="Market Cap")
    market_price = market_span.find_next('div').text if market_span else "N/A"

    volum_span = btc_soup.find('div', string="Volume 24h")
    volum_price = volum_span.find_next('div').text if volum_span else "N/A"

    return JsonResponse({
        'bitcoin_price': bitcoin_price,
        'bitcoin_change': bitcoin_change,
        'market_price': market_price,
        'volum_price': volum_price,
    })