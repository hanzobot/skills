#!/usr/bin/env python3
"""
MILKEE Accounting API Integration
Complete project, customer, time tracking, task & product management
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

# Configuration
API_TOKEN = os.getenv('MILKEE_API_TOKEN', '')
COMPANY_ID = os.getenv('MILKEE_COMPANY_ID', '')
API_BASE = "https://app.milkee.ch/api/v2"

# Timer state file
TIMER_FILE = Path.home() / ".milkee_timer"

def api_call(method, endpoint, data=None):
    """Make API call to MILKEE"""
    if not API_TOKEN or not COMPANY_ID:
        print("❌ Error: MILKEE_API_TOKEN and MILKEE_COMPANY_ID required!")
        return None
    
    url = f"{API_BASE}/companies/{COMPANY_ID}/{endpoint}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method=method
        )
        
        if data:
            req.data = json.dumps(data).encode()
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode())
            print(f"❌ HTTP {e.code}: {error_data.get('message', 'Unknown error')}")
        except:
            print(f"❌ HTTP {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fuzzy_match(search_term, items, key='name'):
    """Fuzzy match search term to items"""
    search_term = search_term.lower()
    
    matches = []
    for item in items:
        name = item.get(key, '').lower()
        ratio = SequenceMatcher(None, search_term, name).ratio()
        if ratio > 0.4:  # 40% threshold
            matches.append((ratio, item))
    
    if matches:
        matches.sort(reverse=True)
        return matches[0][1]
    return None

# ============ PROJECTS ============

def list_projects():
    """List all projects"""
    result = api_call("GET", "projects")
    if not result:
        return
    
    projects = result.get('data', [])
    print(f"\n📋 {len(projects)} Projects:\n")
    
    for p in projects:
        print(f"  • {p.get('name')} (ID: {p.get('id')})")
        if p.get('budget'):
            print(f"    Budget: CHF {p.get('budget')}")
        print()

def create_project(name, customer_id=None, budget=None):
    """Create new project"""
    data = {
        "name": name,
        "customer_id": customer_id,
        "budget": budget,
        "project_type": "byHour"
    }
    
    result = api_call("POST", "projects", data)
    if result:
        project = result.get('data', {})
        print(f"✅ Project created: {project.get('name')} (ID: {project.get('id')})")

def update_project(project_id, name=None, budget=None):
    """Update project"""
    data = {}
    if name:
        data['name'] = name
    if budget:
        data['budget'] = budget
    
    result = api_call("PUT", f"projects/{project_id}", data)
    if result:
        print(f"✅ Project updated")

# ============ CUSTOMERS ============

def list_customers():
    """List all customers"""
    result = api_call("GET", "customers")
    if not result:
        return
    
    customers = result.get('data', [])
    print(f"\n👥 {len(customers)} Customers:\n")
    
    for c in customers:
        print(f"  • {c.get('name')} (ID: {c.get('id')})")
        if c.get('city'):
            print(f"    {c.get('city')}")
        print()

def create_customer(name, city=None, email=None):
    """Create new customer"""
    data = {
        "name": name,
        "city": city,
        "email": email
    }
    
    result = api_call("POST", "customers", data)
    if result:
        customer = result.get('data', {})
        print(f"✅ Customer created: {customer.get('name')} (ID: {customer.get('id')})")

def update_customer(customer_id, name=None, city=None):
    """Update customer"""
    data = {}
    if name:
        data['name'] = name
    if city:
        data['city'] = city
    
    result = api_call("PUT", f"customers/{customer_id}", data)
    if result:
        print(f"✅ Customer updated")

# ============ TIME TRACKING ============

def start_timer(project_search, description=""):
    """Start timer (smart project matching)"""
    # Get projects
    result = api_call("GET", "projects")
    if not result:
        return
    
    projects = result.get('data', [])
    project = fuzzy_match(project_search, projects)
    
    if not project:
        print(f"❌ No project found matching '{project_search}'")
        return
    
    # Save timer state
    timer_data = {
        "project_id": project['id'],
        "project_name": project['name'],
        "description": description,
        "start_time": datetime.now().isoformat()
    }
    
    with open(TIMER_FILE, 'w') as f:
        json.dump(timer_data, f)
    
    print(f"✅ Timer started: {project['name']}")
    if description:
        print(f"   Description: {description}")

def stop_timer():
    """Stop timer and log to MILKEE"""
    if not TIMER_FILE.exists():
        print("❌ No timer running")
        return
    
    with open(TIMER_FILE, 'r') as f:
        timer_data = json.load(f)
    
    start_time = datetime.fromisoformat(timer_data['start_time'])
    end_time = datetime.now()
    duration = end_time - start_time
    
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    
    # Create time entry
    data = {
        "project_id": timer_data['project_id'],
        "date": end_time.strftime("%Y-%m-%d"),
        "hours": hours,
        "minutes": minutes,
        "description": timer_data['description'],
        "billable": True
    }
    
    result = api_call("POST", "times", data)
    
    if result:
        print(f"✅ Time logged: {hours}h {minutes}min on {timer_data['project_name']}")
        TIMER_FILE.unlink()  # Delete timer file
    else:
        print(f"❌ Failed to log time")

def list_times_today():
    """Show today's time entries"""
    today = datetime.now().strftime("%Y-%m-%d")
    result = api_call("GET", f"times?filter[date]={today}")
    
    if not result:
        return
    
    times = result.get('data', [])
    
    print(f"\n⏱️  Time entries for {today}:\n")
    
    total_minutes = 0
    for t in times:
        hours = t.get('hours', 0)
        minutes = t.get('minutes', 0)
        total_minutes += hours * 60 + minutes
        
        print(f"  • {t.get('description', 'No desc')} - {hours}h {minutes}min")
        print(f"    Project: {t.get('project', {}).get('name', 'N/A')}")
    
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    print(f"\n📊 Total: {total_hours}h {remaining_minutes}min\n")

# ============ TASKS ============

def list_tasks(project_id=None):
    """List tasks"""
    endpoint = "tasks"
    if project_id:
        endpoint += f"?filter[project_id]={project_id}"
    
    result = api_call("GET", endpoint)
    if not result:
        return
    
    tasks = result.get('data', [])
    print(f"\n✅ {len(tasks)} Tasks:\n")
    
    for t in tasks:
        print(f"  • {t.get('name')} (ID: {t.get('id')})")
        if t.get('status'):
            print(f"    Status: {t.get('status')}")
        print()

def create_task(name, project_id, description=None):
    """Create task"""
    data = {
        "name": name,
        "project_id": project_id,
        "description": description
    }
    
    result = api_call("POST", "tasks", data)
    if result:
        task = result.get('data', {})
        print(f"✅ Task created: {task.get('name')} (ID: {task.get('id')})")

def update_task(task_id, name=None, status=None):
    """Update task"""
    data = {}
    if name:
        data['name'] = name
    if status:
        data['status'] = status
    
    result = api_call("PUT", f"tasks/{task_id}", data)
    if result:
        print(f"✅ Task updated")

# ============ PRODUCTS ============

def list_products():
    """List products"""
    result = api_call("GET", "products")
    if not result:
        return
    
    products = result.get('data', [])
    print(f"\n📦 {len(products)} Products:\n")
    
    for p in products:
        print(f"  • {p.get('name')} (ID: {p.get('id')})")
        if p.get('price'):
            print(f"    Price: CHF {p.get('price')}")
        print()

def create_product(name, price=None, description=None):
    """Create product"""
    data = {
        "name": name,
        "price": price,
        "description": description
    }
    
    result = api_call("POST", "products", data)
    if result:
        product = result.get('data', {})
        print(f"✅ Product created: {product.get('name')} (ID: {product.get('id')})")

def update_product(product_id, name=None, price=None):
    """Update product"""
    data = {}
    if name:
        data['name'] = name
    if price:
        data['price'] = price
    
    result = api_call("PUT", f"products/{product_id}", data)
    if result:
        print(f"✅ Product updated")

# ============ CLI ============

def main():
    if len(sys.argv) < 2:
        print("MILKEE CLI - Usage:")
        print("  start_timer <project> [description]")
        print("  stop_timer")
        print("  list_times_today")
        print("  list_projects")
        print("  create_project <name> --customer-id X --budget X")
        print("  update_project <id> --name X --budget X")
        print("  list_customers")
        print("  create_customer <name> --city X")
        print("  update_customer <id> --name X")
        print("  list_tasks [--project-id X]")
        print("  create_task <name> --project-id X")
        print("  update_task <id> --name X")
        print("  list_products")
        print("  create_product <name> --price X")
        print("  update_product <id> --price X")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "start_timer":
        project = sys.argv[2] if len(sys.argv) > 2 else ""
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        start_timer(project, description)
    
    elif cmd == "stop_timer":
        stop_timer()
    
    elif cmd == "list_times_today":
        list_times_today()
    
    elif cmd == "list_projects":
        list_projects()
    
    elif cmd == "create_project":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        create_project(name)
    
    elif cmd == "update_project":
        project_id = sys.argv[2] if len(sys.argv) > 2 else ""
        update_project(project_id)
    
    elif cmd == "list_customers":
        list_customers()
    
    elif cmd == "create_customer":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        create_customer(name)
    
    elif cmd == "update_customer":
        customer_id = sys.argv[2] if len(sys.argv) > 2 else ""
        update_customer(customer_id)
    
    elif cmd == "list_tasks":
        list_tasks()
    
    elif cmd == "create_task":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        create_task(name, 1)  # Default project_id
    
    elif cmd == "update_task":
        task_id = sys.argv[2] if len(sys.argv) > 2 else ""
        update_task(task_id)
    
    elif cmd == "list_products":
        list_products()
    
    elif cmd == "create_product":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        create_product(name)
    
    elif cmd == "update_product":
        product_id = sys.argv[2] if len(sys.argv) > 2 else ""
        update_product(product_id)
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
