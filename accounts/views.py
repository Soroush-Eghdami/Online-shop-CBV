from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import View, TemplateView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Wishlist


class RegisterView(View):
    template_name = 'accounts/register.html'
    
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for the user
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('shop:product_list')
        return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')
    
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        
        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        
        # Get user's recent orders
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user)[:5]
        
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'recent_orders': recent_orders
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        
        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('accounts:profile')
        
        # Get user's recent orders
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user)[:5]
        
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'recent_orders': recent_orders
        }
        return render(request, self.template_name, context)


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'accounts/wishlist.html'
    context_object_name = 'wishlist_items'
    login_url = reverse_lazy('accounts:login')
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class AddToWishlistView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')
    
    def post(self, request, product_id):
        from shop.models import Product
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            messages.success(request, f'{product.name} added to your wishlist!')
        else:
            messages.info(request, f'{product.name} is already in your wishlist!')
        
        return redirect('accounts:wishlist')


class RemoveFromWishlistView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')
    
    def post(self, request, product_id):
        from shop.models import Product
        product = get_object_or_404(Product, id=product_id)
        
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            messages.success(request, f'{product.name} removed from your wishlist!')
        except Wishlist.DoesNotExist:
            messages.error(request, 'Item not found in your wishlist!')
        
        return redirect('accounts:wishlist')


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'accounts/change_password.html'
    login_url = reverse_lazy('accounts:login')
    
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


