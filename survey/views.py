from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Survey, Question, Response, Answer
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            return render(request, 'survey/login.html', {'error': 'Invalid credentials'})
    return render(request, 'survey/login.html', {'next': request.GET.get('next', '/')})

def custom_logout(request):
    logout(request)
    return redirect('login')

def survey_list(request):
    surveys = Survey.objects.all()
    if not surveys:
        surveys_data = {
            "Competitive Tendering": [
                {"text": "Have you heard about the advantages of competitive tendering, where several suitable contractors are given a package of documents and asked to come up with a price bid within a few weeks. Usually, the contractor who offers the cheapest price is chosen?", "text_required_if_yes": True},
                {"text": "Do you know that the approach in 2.1 provides the lowest price at the outset, but it can result in a contractor having under-priced the work, subsequently looking for ways to inflate the price or experience financial difficulties?"},
                {"text": "Are you aware that the competitive tendering method requires careful preparation of comprehensive drawings, specifications and preferably bills of quantities, upon which a contractor can base his price?"},
                {"text": "Are you aware that tendering by several firms, each with its own subcontractors, will result in about 90% of the resources committed to the process being wasted, since there is only one winning main contractor?", "text_required_if_yes": True},  # Changed
                {"text": "Have you noticed that contractors are invited through an announcement in public media?"},
                {"text": "Do you know that a large number of contractors responded?"},
                {"text": "Are you aware that public agencies are forced to use open tendering?"},
                {"text": "Do you agree that the lowest bid is awarded to the job?"},
                {"text": "The lowest bid contractor may fail to complete the project. If so, what would be the advantage to continue with this method?", "text_required_if_yes": True},  # Changed
                {"text": "In obtaining the lowest possible price, what is your opinion in relation to this?", "has_bid": True},
                {"text": "In this type of tendering, it is not possible to form bid rings. Does this advantage overcome its gaps?", "text_required_if_yes": True},  # Changed
                {"text": "What is your comment?", "text_required_if_yes": True},
            ],
            "Selective Tendering": [
                {"text": "Have you noticed contractors are invited through an announcement in public media?"},
                {"text": "Are you aware that only qualified contractors are allowed to bid?"},
                {"text": "Have you any idea that the owner prepares a short list of prequalified contractors for such type of contract award process?"},
                {"text": "Why do we have a limited number of contractors to bid in the project as compared to open tendering?", "text_required_if_yes": True},  # Changed
                {"text": "Do you know that it is possible to form bid rings between bidders in selective tendering processes?"},
                {"text": "Have you any idea when or for what type of projects this is used for?", "text_required_if_yes": True},  # Changed
                {"text": "Can we use this approach for important projects?"},
                {"text": "Do you think that the quality of work is guaranteed through prequalification for this approach?", "text_required_if_yes": True},  # Changed
            ],
            "Negotiated Tendering": [
                {"text": "Do you know that in this method, the client and advisers consider which contractors are best suited to the type of work?"},
                {"text": "What is your opinion in relation to allowing trusted contractors to be invited to bid in the project by mail or direct contact?", "text_required_if_yes": True},  # Changed
                {"text": "Do you think that it is a good option after 5.2 above that the selected one is then interviewed to determine their keenness and possible contribution to the team?", "text_required_if_yes": True},  # Changed
                {"text": "Do we have an option if negotiations over prices break down at this early stage, another contractor is selected in this approach?", "text_required_if_yes": True},  # Changed
                {"text": "The approach provides an option for the quantity surveyor to work with the contractor to update the cost plan or budget and report to the team. How can this be achieved in ERA?", "text_required_if_yes": True},  # Changed
                {"text": "What type of projects are suitable for negotiated tendering?", "text_required_if_yes": True},  # Changed
            ]
        }
        for title, questions_list in surveys_data.items():
            survey = Survey.objects.create(title=title)
            for q in questions_list:
                Question.objects.create(
                    survey=survey,
                    text=q["text"],
                    has_text_response=q.get("has_text_response", False),
                    has_bid=q.get("has_bid", False),
                    text_required_if_yes=q.get("text_required_if_yes", False)
                )
        surveys = Survey.objects.all()
    return render(request, 'survey/survey_list.html', {'surveys': surveys})

def survey_view(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    questions = Question.objects.filter(survey=survey)

    if request.method == 'POST':
        errors = []
        response = Response.objects.create(
            user=request.user if request.user.is_authenticated else None,
            survey=survey
        )
        for question in questions:
            yes_no = request.POST.get(f'yes_no_{question.id}')
            text = request.POST.get(f'text_{question.id}', '')
            bid_amount = request.POST.get(f'bid_{question.id}', None) if question.has_bid else None

            # Validation
            if yes_no not in ['True', 'False']:
                errors.append(f"Please answer Yes/No for: {question.text}")
            else:
                if question.has_text_response and not text.strip():
                    errors.append(f"Please provide a response for: {question.text}")
                elif question.text_required_if_yes and yes_no == 'True' and not text.strip():
                    errors.append(f"Please provide an opinion for: {question.text}")
            if question.has_bid and (not bid_amount or float(bid_amount) <= 0):
                errors.append(f"Please enter a valid bid amount for: {question.text}")

            if not errors:
                Answer.objects.create(
                    response=response,
                    question=question,
                    yes_no=yes_no == 'True',
                    text=text if text.strip() else None,
                    bid_amount=bid_amount if bid_amount else None
                )

        if errors:
            response.delete()
            return render(request, 'survey/survey.html', {'survey': survey, 'questions': questions, 'errors': errors})
        return redirect('survey_success')

    return render(request, 'survey/survey.html', {'survey': survey, 'questions': questions})

def survey_success(request):
    return render(request, 'survey/success.html')

@login_required
def dashboard(request):
    responses = Response.objects.all()
    bid_data = Answer.objects.filter(bid_amount__isnull=False).values('bid_amount', 'question__text')
    questions = Question.objects.all()
    yes_no_data = {}
    for question in questions:
        yes_count = Answer.objects.filter(question=question, yes_no=True).count()
        no_count = Answer.objects.filter(question=question, yes_no=False).count()
        yes_no_data[question.text] = {'yes': yes_count, 'no': no_count}
    return render(request, 'survey/dashboard.html', {'responses': responses, 'bid_data': bid_data, 'yes_no_data': yes_no_data})

@login_required
def generate_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.blue)
    p.drawString(100, 750, "Ethiopian Roads Administration Survey Report")
    responses = Response.objects.all()
    y = 720
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    for resp in responses:
        user_info = resp.user.username if resp.user else "Anonymous"
        p.drawString(50, y, f"Respondent: {user_info}")
        y -= 20
        p.setFont("Helvetica-Oblique", 10)
        for ans in resp.answer_set.all():
            answer_text = f"Q: {ans.question.text[:50]}... - {'Yes' if ans.yes_no else 'No' if ans.yes_no is not None else 'N/A'}"
            if ans.text:
                answer_text += f" - Text: {ans.text[:50]}..."
            if ans.bid_amount:
                answer_text += f" - Bid: {ans.bid_amount}"
            p.drawString(70, y, answer_text)
            y -= 15
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = 750
        p.setFont("Helvetica", 12)
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')