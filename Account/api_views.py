import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from Account.forms import AccountAuthentication, RegistrationForm
from Account.models import Account


def register(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(
            json.dumps({"error": "You've already signed in!"}),
            content_type="application/json",
        )
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data["email"].lower()
            raw_password = form.cleaned_data["password1"]
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return HttpResponse(json.dumps({"result": "Done!"}))
        else:
            return HttpResponse(
                json.dumps({"errors": form.errors}), content_type="application/json"
            )


def login_view(request):
    if request.POST:
        form = AccountAuthentication(request.POST)
        if form.is_valid():
            email = request.POST["email"]
            password = request.POST["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return HttpResponse(
                    json.dumps({"result": "Done!"}), content_type="application/json"
                )
            return HttpResponse(
                json.dumps({"error": "Something went wrong!"}),
                content_type="application/json",
            )
        return HttpResponse(
            json.dumps({"error": form.errors}), content_type="application/json"
        )


def check_email(request):
    if request.POST:
        email = request.POST.get("email", None)
        if email != None:
            find = Account.objects.filter(email=email)
            return HttpResponse(
                json.dumps({"result": len(find) == 0}), content_type="application/json"
            )
