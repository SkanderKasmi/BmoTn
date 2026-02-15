from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import webbrowser
import subprocess
import platform
import os

app = FastAPI(title="BMO Task Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    action: str  # "open_app", "search", "open_url"
    target: str  # App name, search query, or URL
    parameters: Optional[Dict] = None

class TaskResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None

# Common app mappings
APP_MAPPINGS = {
    "youtube": {
        "windows": "start https://www.youtube.com",
        "darwin": "open https://www.youtube.com",
        "linux": "xdg-open https://www.youtube.com",
        "android": "intent://www.youtube.com#Intent;scheme=https;package=com.google.android.youtube;end"
    },
    "facebook": {
        "windows": "start https://www.facebook.com",
        "darwin": "open https://www.facebook.com",
        "linux": "xdg-open https://www.facebook.com",
        "android": "intent://www.facebook.com#Intent;scheme=https;package=com.facebook.katana;end"
    },
    "whatsapp": {
        "windows": "start https://web.whatsapp.com",
        "darwin": "open https://web.whatsapp.com",
        "linux": "xdg-open https://web.whatsapp.com",
        "android": "intent://send#Intent;scheme=https;package=com.whatsapp;end"
    },
    "gmail": {
        "windows": "start https://mail.google.com",
        "darwin": "open https://mail.google.com",
        "linux": "xdg-open https://mail.google.com",
        "android": "intent://mail.google.com#Intent;scheme=https;package=com.google.android.gm;end"
    },
    "maps": {
        "windows": "start https://maps.google.com",
        "darwin": "open https://maps.google.com",
        "linux": "xdg-open https://maps.google.com",
        "android": "intent://maps.google.com#Intent;scheme=https;package=com.google.android.apps.maps;end"
    },
    "chrome": {
        "windows": "start chrome",
        "darwin": "open -a 'Google Chrome'",
        "linux": "google-chrome",
        "android": "intent://#Intent;package=com.android.chrome;end"
    },
    "calculator": {
        "windows": "calc",
        "darwin": "open -a Calculator",
        "linux": "gnome-calculator",
        "android": "intent://#Intent;package=com.google.android.calculator;end"
    }
}

def get_system():
    """Detect operating system"""
    return platform.system().lower()

@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute a task (open app, search, etc.)"""
    try:
        if request.action == "open_app":
            return await open_app(request.target)
        elif request.action == "search":
            return await search_web(request.target)
        elif request.action == "open_url":
            return await open_url(request.target)
        else:
            raise HTTPException(status_code=400, detail="Unknown action")
            
    except Exception as e:
        return TaskResponse(
            success=False,
            message=f"Failed to execute task: {str(e)}"
        )

async def open_app(app_name: str) -> TaskResponse:
    """Open an application"""
    app_name = app_name.lower().strip()
    system = get_system()
    
    # Check if app is in mappings
    if app_name in APP_MAPPINGS:
        command = APP_MAPPINGS[app_name].get(system)
        if command:
            try:
                if system == "windows":
                    os.system(command)
                else:
                    subprocess.Popen(command, shell=True)
                
                return TaskResponse(
                    success=True,
                    message=f"فتحت {app_name} إلك! 🎮" if system != "android" else f"Opening {app_name}",
                    details={"app": app_name, "platform": system}
                )
            except Exception as e:
                return TaskResponse(
                    success=False,
                    message=f"ماقدرتش نفتح {app_name}: {str(e)}"
                )
    
    # Try direct launch
    try:
        if system == "windows":
            os.system(f"start {app_name}")
        elif system == "darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen([app_name])
        
        return TaskResponse(
            success=True,
            message=f"نسيت نفتح {app_name}! 🎮"
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message=f"ماعرفتش هذا البرنامج. قلّي كيفاش نفتحو؟"
        )

async def search_web(query: str) -> TaskResponse:
    """Perform a web search"""
    try:
        search_url = f"https://www.google.com/search?q={query}"
        system = get_system()
        
        if system == "windows":
            os.system(f"start {search_url}")
        elif system == "darwin":
            subprocess.Popen(["open", search_url])
        else:
            subprocess.Popen(["xdg-open", search_url])
        
        return TaskResponse(
            success=True,
            message=f"هاني نبحثلك على '{query}'! 🔍",
            details={"query": query, "url": search_url}
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message=f"مشكلة في البحث: {str(e)}"
        )

async def open_url(url: str) -> TaskResponse:
    """Open a URL in browser"""
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        webbrowser.open(url)
        
        return TaskResponse(
            success=True,
            message=f"فتحتلك الموقع! 🌐",
            details={"url": url}
        )
    except Exception as e:
        return TaskResponse(
            success=False,
            message=f"ماقدرتش نفتح الموقع: {str(e)}"
        )

@app.get("/apps/list")
async def list_apps():
    """List available apps"""
    return {
        "apps": list(APP_MAPPINGS.keys()),
        "custom_apps_supported": True
    }

@app.post("/android/intent")
async def android_intent(request: TaskRequest):
    """Generate Android intent for app launching"""
    app_name = request.target.lower()
    
    if app_name in APP_MAPPINGS:
        intent = APP_MAPPINGS[app_name].get("android")
        if intent:
            return {
                "intent": intent,
                "app": app_name
            }
    
    return {
        "error": "App not found",
        "app": app_name
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bmo-task"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
