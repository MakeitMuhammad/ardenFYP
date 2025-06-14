from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse
import json
import requests
from openai import OpenAI
from django.shortcuts import get_object_or_404
from .models import UserProfile, Project, ProjectTask, Tag, CustomUser, Message, Notification
import json
import os
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import Message
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from collections import OrderedDict
import os


# Create your views here.


#-------------------------------------------------
#index
#-------------------------------------------------
def index(request):
    return render(request, 'index.html')


#-------------------------------------------------
#about
#-------------------------------------------------
def about(request):
    return render(request, 'about.html')


#-------------------------------------------------
#contact
#-------------------------------------------------
def contact(request):
    if request.method == "POST":
        # Get form data from the POST request
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Combine form data into a full email message
        full_message = f"From: {name} <{email}>\n\n{message}"

        # Send email to your inbox
        send_mail(subject, full_message, email, ['mohammadtalat163@gmail.com'])

        # Show a success message
        messages.success(request, "Your message has been sent successfully!")

    # If the request is not POST, show the empty form
    return render(request, "contact.html")












#-------------------------------------------------
#dashboard
#-------------------------------------------------
@login_required(login_url='login')  # 'login' should match the name in your URLconf
def dashboard(request):
     projects = Project.objects.filter(user=request.user).prefetch_related('projecttask_set')

     for project in projects:
        # Attach the first pending task to each project object
        pending_task = project.projecttask_set.filter(status="pending").first()
        project.pending_task = pending_task

     

   
     return render(request, "dashboard.html", {"projects": projects}, )
#-------------------------------------------------
#profile update
#-------------------------------------------------
@csrf_exempt  # or use @login_required(login_url='login') + CSRF token as you're doing in JS
@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user = request.user
            profile = user.userprofile

            # Update user fields
            user.full_name = data.get('full_name', user.full_name)
            user.email = data.get('email', user.email)
            user.save()

            # Update userprofile fields
            profile.phone = data.get('phone', profile.phone)
            profile.mobile = data.get('mobile', profile.mobile)
            profile.address = data.get('address', profile.address)
            profile.qualification = data.get('qualification', profile.qualification)
            profile.last_work_company = data.get('last_work_company', profile.last_work_company)
            profile.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


#-------------------------------------------------
#profile picute update
#-------------------------------------------------
import logging
import cloudinary.uploader
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        try:
            upload_result = cloudinary.uploader.upload(
                request.FILES['profile_pic'],
                folder='profile_pics/'  # Optional: put uploads into a specific folder
            )

            profile_url = upload_result.get('secure_url')
            if not profile_url:
                raise Exception("Cloudinary did not return a URL")

            user_profile = request.user.userprofile
            user_profile.profile_pic_url = profile_url
            user_profile.save()

            return JsonResponse({'success': True, 'url': profile_url})
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'No file uploaded'})

#-------------------------------------------------
#social links
#-------------------------------------------------
@login_required(login_url='login')  
@csrf_exempt
def update_social_link(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            # Get the social links via related_name
            profile = request.user.social_link

            # Validate and update the field
            if hasattr(profile, field):
                setattr(profile, field, value)
                profile.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid field'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

#-------------------------------------------------
#dashboard task alerts and comlete
#-------------------------------------------------
@login_required(login_url='login')
def complete_task(request, task_id):
    task = get_object_or_404(ProjectTask, id=task_id, project__user=request.user)
    if request.method == "POST":
        task.status = "completed"
        task.save()
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


   




#---------------------------------------------------
#expert dashboard
#---------------------------------------------------
@login_required(login_url='login')
def expert_dashboard(request):
    if request.user.account_type == 'expert':
        tags = Tag.objects.filter(user=request.user)
        unread_count = request.user.notifications.filter(is_read=False).count() 

        context = {
            'tags': tags,
            'user': request.user,
            'unread_count': unread_count  # ✅ include in context
        }
        return render(request, 'dashboard-exp.html', context)
    else:
        return render(request, 'dashboard.html')
#-------------------------------------------------
#tags
#-------------------------------------------------
@login_required(login_url='login')
def add_skills(request):
    if request.method == 'POST':
        skill_name = request.POST.get('name', '').strip().upper()  # Convert to uppercase
        
        if skill_name:
            Tag.objects.create(user=request.user, name=skill_name)
            messages.success(request, f"Skill '{skill_name}' added successfully.")
        else:
            messages.error(request, "Skill name cannot be empty.")

    return redirect('expert_dashboard')  








#-------------------------------------------------
#aibuddy
#-------------------------------------------------


import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Renders the template with correct base
@login_required(login_url='login')
def aibuddy(request):
    base_template = 'base3.html' if request.user.account_type == "expert" else 'base2.html'
    return render(request, 'aibuddy.html', {'base_template': base_template})


# Handles chat API
@csrf_exempt
def aibuddy_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "⚠️ Please enter a message."})

            payload = {
                "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }

            headers = {
                # "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=15
            )

            if response.status_code != 200:
             return JsonResponse({
             "reply": f"❌ Model API error {response.status_code}: {response.text}"
     })
            

            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": f"❌ Server error: {str(e)}"})

    return JsonResponse({"reply": "❌ Invalid request method."})







#------------------------------------------------
#Project
#------------------------------------------------
@login_required(login_url='login')
def projects(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects.html', {'projects': projects})
#-------------------------------------------------
#new projects
#-------------------------------------------------
@login_required(login_url='login')
def newproject(request):
    questions = [
        {"text": "What is your business idea or product/service?", "example": "e.g., Online handmade jewelry store"},
        {"text": "Who is your target customer or audience?", "example": "e.g., Women aged 18–35 interested in fashion"},
        {"text": "What problem are you solving for your customers?", "example": "e.g., Limited access to unique, affordable handmade accessories"},
        {"text": "How do you plan to make money (business model)?", "example": "e.g., Selling products directly via Shopify"},
        {"text": "Do you plan to start online, offline, or both?", "example": "e.g., Online only at the start"},
        {"text": "What is your current budget or financial plan for starting?", "example": "e.g., I have $2,000 saved for initial inventory and website"},
        {"text": "Do you have any team members, or will you start solo?", "example": "e.g., Starting solo, but my sister will help with designs"},
        {"text": "What skills or tools do you currently have to build or run this business?", "example": "e.g., Basic Photoshop and social media marketing skills"},
        {"text": "What is your timeline for launching?", "example": "e.g., Hoping to launch within 3 months"},
        {"text": "What are your biggest fears, obstacles, or areas where you need help?", "example": "e.g., Struggling with marketing and building an audience"},
    ]
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if title and description:
            # Create project
            project = Project.objects.create(user=request.user, title=title, description=description)

            # Build prompt
            answers = []
            for i in range(1, len(questions) + 1):
                answer = request.POST.get(f'answer_{i}', '')
                answers.append(f"{questions[i-1]['text']} Answer: {answer}")

            prompt = (
                "Based on the following business information, list only the exact actionable tasks in numbered format "
                "needed to start and launch the business no headings no footer no starting message just list of tasks:\n\n"
                + "\n".join(answers)
            )

            # Call OpenRouter API using `requests`
            try:
                headers = {
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
                    "messages": [
                        {"role": "system", "content": "You are a startup mentor helping break down business ideas into tasks."},
                        {"role": "user", "content": prompt}
                    ]
                }

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=120
                )

                if response.status_code != 200:
                    raise Exception(f"OpenRouter error {response.status_code}: {response.text}")

                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                task_list = [line.strip("-•0123456789. ").strip() for line in content.split('\n') if line.strip()]

                # Save tasks
                for task in task_list:
                    if task:
                        ProjectTask.objects.create(project=project, task=task)

                return redirect("projects")

            except Exception as e:
                messages.error(request, f"AI task generation failed: {str(e)}")
                return redirect("newproject")

    projects = Project.objects.filter(user=request.user)
    return render(request, 'newproject.html', {'questions': questions, 'projects': projects})



      

#     if request.method == 'POST':
#         title = request.POST.get('title')
#         description = request.POST.get('description')

#         if title and description:
#             # Create the project
#             project = Project.objects.create(user=request.user, title=title, description=description)

#             # Collect all answers
#             answers = []
#             for i in range(1, len(questions) + 1):
#                 answer = request.POST.get(f'answer_{i}', '')
#                 answers.append(f"{questions[i-1]['text']} Answer: {answer}")

#             # Build the prompt
#             prompt = "Based on the following business information, list only the exact actionable tasks in numbered format needed to start and launch the business no headings no footer no starting message just list of tasks :\n\n" + "\n".join(answers)

#             # Call OpenAI
#             print("ENV DEBUG:", os.getenv("OPENROUTER_API_KEY"))
#             client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_API_KEY")
# )

#             # Create chat completion
#         #test
#         try:

#             completion = client.chat.completions.create(
#                 model="deepseek/deepseek-r1:free",
#                 messages=[
#                     {"role": "system", "content": "You are a startup mentor helping break down business ideas into tasks."},
#                     {"role": "user", "content": prompt}
#                 ],timeout=120
#             )

#             # Extract tasks from response
#             content = completion.choices[0].message.content.strip()
#             task_list = [line.strip("-•0123456789. ") for line in content.split('\n') if line.strip()]
#        #test
#         except Exception as e:
#             messages.error(request, f"AI task generation failed: {e}")
#             return redirect("newproject") 
#         #---

#             # Save tasks to DB
#             for task in task_list:
#                 if task:
#                     ProjectTask.objects.create(project=project, task=task)

#             return redirect("projects")  # Only happens after POST success

   
#     projects = Project.objects.filter(user=request.user)
#     return render(request, 'newproject.html', {'questions': questions, 'projects': projects})

      

#-------------------------------------------------
#project tasks
#-------------------------------------------------
@login_required(login_url='login')
def project_tasks(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tasks = project.projecttask_set.all()  # Or use related_name if defined
    return render(request, 'tasks.html', {'project': project, 'tasks': tasks})

#-------------------------------------------------
#user search
#-------------------------------------------------
@login_required(login_url='login')
def user_search(request):
    query = request.GET.get('q', '')
    mode = request.GET.get('mode', 'name')

    if query:
        if mode == 'skill':
            user_ids = Tag.objects.filter(name__icontains=query).values_list('user_id', flat=True).distinct()
            users = CustomUser.objects.filter(id__in=user_ids, account_type='expert')
        else:  # name
            users = CustomUser.objects.filter(full_name__icontains=query, account_type='expert')
    else:
        users = CustomUser.objects.none()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{'id': user.id, 'name': user.full_name} for user in users]
        return JsonResponse({'results': data})

    return render(request, 'search.html', {'users': users})

#-------------------------------------------------
#profile view
#-------------------------------------------------
@login_required(login_url='login')
def profile_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'profile_view.html', {'profile_user': user})

#-------------------------------------------------
# message
#-------------------------------------------------


User = get_user_model()

@login_required(login_url='login')

def message_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    base_template = 'base3.html' if current_user.account_type == "expert" else 'base2.html'

    # send a notification
    if other_user != current_user:
        send_notification(
            request=request,
            sender=current_user,
            recipient=other_user,
            message=f"{current_user.full_name} has messaged you.",
            link=request.build_absolute_uri()  # current full URL
        )
         # ✅ Mark unread messages from other_user to current_user as read
    Message.objects.filter(sender=other_user, recipient=current_user, read=False).update(read=True)


    # Get all messages between the two users
    messages = Message.objects.filter(  
        (Q(sender=current_user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=current_user))
    ).order_by('timestamp')
    

    return render(request, 'message.html', {
        'base_template': base_template,
        'other_user': other_user,
        'messages': messages
    }
    )



@login_required(login_url='login')
@require_POST
@csrf_exempt  # Optional: use if CSRF token is not being sent via AJAX
def send_message(request):
    data = json.loads(request.body)
    recipient_id = data.get('recipient_id')
    content = data.get('content')

    recipient = get_object_or_404(User, id=recipient_id)

    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content
    )

    # Optional: send notification on new message
    send_notification(
        request=request,
        sender=request.user,
        recipient=recipient,
        message=f"You have a new message from {request.user.full_name}",
        link=None
    )

    return JsonResponse({
        'id': message.id,
        'sender': message.sender.full_name,
        'content': message.content,
        'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    })


#-------------------------------------------------
# notification logic
#-------------------------------------------------

@login_required(login_url='login')
def send_notification(request, sender, recipient, message, link=None):
    """
    Send a notification from sender to recipient for every message.
    Only the recipient gets the notification. No duplication logic.
    """

    # Only generate chat link if not provided
    if not link:
        chat_url = reverse('message_view', args=[sender.id])
        link = request.build_absolute_uri(chat_url)

    # Always send notification to the recipient
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        message=message,
        link=link
    )


#-------------------------------------------------
# notification view
#-------------------------------------------------

@login_required(login_url='login')
def notification_list(request):
    notifications = request.user.notifications.order_by('-timestamp')  # assumes related_name='notifications'
    notifications.update(is_read=True)
    return render(request, 'notification.html', {
        'notifications': notifications
    })




#-------------------------------------------------
# all chats
#-------------------------------------------------
@login_required(login_url='login')
def all_chats(request):
    user = request.user

    # Get all messages received by this user, newest first
    received_messages = Message.objects.filter(recipient=user).order_by('-timestamp')

    # Use OrderedDict to keep latest message from each sender
    latest_per_sender = OrderedDict()
    for msg in received_messages:
        if msg.sender.id not in latest_per_sender:
            latest_per_sender[msg.sender.id] = msg

    return render(request, 'allchats.html', {
        'latest_messages': latest_per_sender.values()
    })


#-------------------------------------------------
# returns
#-------------------------------------------------
@login_required(login_url='login')
#returns you to dashboard if your account type = user if account type is expert then it returns you to expert dashboard
def returns(request):
    if request.user.account_type == "expert":
        return redirect('expert_dashboard')
    else:
        return redirect('dashboard')

#-------------------------------------------------
#delete logic
#-------------------------------------------------
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project.delete()
    return redirect('returns') 

@login_required
def delete_account(request):
    user = request.user
    user.delete()
    return redirect('returns')  

@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Tag, id=skill_id, user=request.user)
    skill.delete()
    return redirect('returns')  


    

    

































#-------------------------------------------------
#signup
#-------------------------------------------------
def signup(request):
    return render(request, 'signup.html')

#signupform
User = get_user_model()

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        account_type = request.POST.get('account_type')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'signup.html')

        # Create the user
        user = User.objects.create(
            username=email, #check if this is necessary step
            email=email,
            full_name=full_name,
            account_type=account_type,
            password=make_password(password)
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    # Show the signup form
    return render(request, 'signup.html')


#-------------------------------------------------
#login
#-------------------------------------------------
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using username (assuming username = email)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful.")

            # Redirect based on account type
            if user.account_type == "expert":
                return redirect('expert_dashboard')  # Use URL name here
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')

#-------------------------------------------------
#logout
#-------------------------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Redirect to login page after logout

#-------------------------------------------------
# base template
#-------------------------------------------------
@login_required(login_url='login')
def aibuddy(request):
    if request.user.account_type == "expert":
        base_template = 'base3.html'
    else:
        base_template = 'base2.html'

    return render(request, 'aibuddy.html', {
        'base_template': base_template
    })

