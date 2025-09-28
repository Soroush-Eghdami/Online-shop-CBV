from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


class OrderCreateView(View):
    template_name = 'orders/order/create.html'
    success_template = 'orders/order/created.html'
    
    def get(self, request):
        cart = Cart(request)
        form = OrderCreateForm()
        
        if request.user.is_authenticated:
            # Pre-fill form with user data
            form.fields['first_name'].initial = request.user.first_name
            form.fields['last_name'].initial = request.user.last_name
            form.fields['email'].initial = request.user.email
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                form.fields['address'].initial = profile.address
                form.fields['city'].initial = profile.city
                form.fields['postal_code'].initial = profile.postal_code
        
        return render(request, self.template_name, {'cart': cart, 'form': form})
    
    def post(self, request):
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        
        if form.is_valid():
            # Create the order manually since OrderCreateForm is not a ModelForm
            order_data = form.cleaned_data
            
            if request.user.is_authenticated:
                # Use user data if available, otherwise use form data
                order = Order.objects.create(
                    user=request.user,
                    first_name=request.user.first_name or order_data['first_name'],
                    last_name=request.user.last_name or order_data['last_name'],
                    email=request.user.email or order_data['email'],
                    address=request.user.profile.address if hasattr(request.user, 'profile') and request.user.profile.address else order_data['address'],
                    city=request.user.profile.city if hasattr(request.user, 'profile') and request.user.profile.city else order_data['city'],
                    postal_code=request.user.profile.postal_code if hasattr(request.user, 'profile') and request.user.profile.postal_code else order_data['postal_code'],
                )
            else:
                # Create order for anonymous user
                order = Order.objects.create(
                    first_name=order_data['first_name'],
                    last_name=order_data['last_name'],
                    email=order_data['email'],
                    address=order_data['address'],
                    city=order_data['city'],
                    postal_code=order_data['postal_code'],
                )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear the cart
            cart.clear()
            return render(request, self.success_template, {'order': order})
        
        return render(request, self.template_name, {'cart': cart, 'form': form})


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order/list.html'
    context_object_name = 'orders'
    login_url = reverse_lazy('accounts:login')
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order/detail.html'
    context_object_name = 'order'
    login_url = reverse_lazy('accounts:login')
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

