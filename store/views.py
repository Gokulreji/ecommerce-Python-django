from store.models import Customer, Order, OrderItems, Product, ShippingAddress
from django.shortcuts import render
from django.http import JsonResponse
import json,datetime
from . utils import cookieCart,cartData, guestOrder
def store(request):
    data = cartData(request)
    cartItem = data['cartItem']
    

    products = Product.objects.all()
    context = {'product':products, 'cartItem':cartItem}
    return render(request, 'store.html', context)

def cart(request):
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItem':cartItem}
    return render(request, 'cart.html', context)

def checkout(request): 
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItem':cartItem}
    return render(request, 'checkout.html', context)

def UpdateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItems.objects.get_or_create(order = order,product = product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0 :
        orderItem.delete()    

    return JsonResponse('Item  was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order = order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:

        ShippingAddress.objects.create(
            Customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )

    return JsonResponse('payment completed', safe= False)