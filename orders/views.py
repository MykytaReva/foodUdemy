from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from menu.models import FoodItem
from marketplace.models import Tax
import simplejson as json
from .utils import generate_order_number
from django.http import HttpResponse, JsonResponse
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def place_order(request):
    # place order
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)

    # Calculate tax data
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    k = {}
    total_data = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal

        tax_dict = {}

        for z in get_tax:
            tax_type = z.tax_type
            tax_percentage = z.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        # Construct total data
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})


    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    total = get_cart_amount(request)['total']
    tax_data = get_cart_amount(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = total

            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,


            }

            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    # check if the request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status = status,
        )
        payment.save()
        # update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # move the cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()

        # send order confirmation email to the customer
        mail_subject = 'Thank you for the purchase!!!'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,

        }
        send_notification(mail_subject, mail_template, context)
        # send order received email to the vendor
        mail_subject = '<h3>You have a new order!!!</h3>'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        context = {
            'order': order,
            'to_email': to_emails,

        }
        print(to_emails)
        send_notification(mail_subject, mail_template, context)
        # clear the cart if the payment is success
        cart_items.delete()
        # return back to ajax with the status success or failure
        response = {
            'order_numer': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)



    return HttpResponse('Payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True
        )
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal':subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)

    except:
        return redirect('home')

