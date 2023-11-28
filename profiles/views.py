import copy

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from . import forms, models


class ProfileBase(View):
    template_name = 'profiles/profile.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.cart = copy.deepcopy(self.request.session.get('cart', {}))

        self.site_profile = None

        if self.request.user.is_authenticated:
            self.site_profile = models.Profile.objects.filter(
                site_user=self.request.user
            ).first()

            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    site_user=self.request.user,
                    instance=self.request.user
                ),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None,
                    instance=self.site_profile
                )
            }
        else:
            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None
                )
            }

        self.userform = self.context['userform']
        self.profileform = self.context['profileform']

        self.rendering = render(self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return self.rendering


class Profile(ProfileBase):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.profileform.is_valid():
            messages.error(
                self.request,
                'There are errors in the register form. Please check if '
                'all fields were filled in correctly.'
            )

            return self.rendering

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # Logged in user
        if self.request.user.is_authenticated:
            site_user = get_object_or_404(
                User, username=self.request.user.username)

            site_user.username = username

            if password:
                site_user.set_password(password)

            site_user.email = email
            site_user.first_name = first_name
            site_user.last_name = last_name
            site_user.save()

            if not self.site_profile:
                self.profileform.cleaned_data['site_user'] = site_user
                site_profile = models.Profile(**self.profileform.cleaned_data)
                site_profile.save()
            else:
                site_profile = self.profileform.save(commit=False)
                site_profile.site_user = site_user
                site_profile.save()

        # Not logged in user (new user)
        else:
            site_user = self.userform.save(commit=False)
            site_user.set_password(password)
            site_user.save()

            site_profile = self.profileform.save(commit=False)
            site_profile.site_user = site_user
            site_profile.save()

        if password:
            session_auth = authenticate(
                self.request,
                username=site_user,
                password=password
            )

            if session_auth:
                login(self.request, user=site_user)

        self.request.session['cart'] = self.cart
        self.request.session.save()

        messages.success(
            self.request,
            'Succesfully registered / updated!'
        )

        return redirect('product:cart')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Username and/or password must not be empty.'
            )
            return redirect('profiles:profile')

        site_user = authenticate(
            self.request, username=username, password=password)

        if not site_user:
            messages.error(
                self.request,
                'Invalid username and/or password.'
            )
            return redirect('profiles:profile')

        login(self.request, user=site_user)

        messages.success(
            self.request,
            'Successfully logged in!'
        )
        return redirect('product:product_list')


class Logout(View):
    def get(self, *args, **kwargs):
        cart = copy.deepcopy(self.request.session.get('cart'))

        logout(self.request)

        self.request.session['cart'] = cart
        self.request.session.save()

        return redirect('product:product_list')
