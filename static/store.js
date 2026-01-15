// Store Frontend JavaScript
// File: static/store.js

let cart = [];
let currentProducts = [];
let currentFilters = {};

// Initialize store
async function initStore() {
    await loadCategories();
    await loadProducts();
    updateCartCount();
    loadCartFromStorage();
}

// Load cart from memory (no localStorage)
function loadCartFromStorage() {
    // Cart is stored in memory only - resets on page refresh
    updateCartCount();
}

// Load product categories
async function loadCategories() {
    try {
        const res = await fetch('/api/store/categories');
        const data = await res.json();
        const container = document.getElementById('category-filters');
        container.innerHTML = '';
        
        data.categories.forEach(category => {
            const label = document.createElement('label');
            label.className = 'flex items-center gap-2 mb-2 cursor-pointer';
            label.innerHTML = `
                <input type="checkbox" name="category" value="${category}" class="rounded">
                <span class="text-sm">${category.charAt(0).toUpperCase() + category.slice(1)}</span>
            `;
            container.appendChild(label);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load products with filters
async function loadProducts() {
    const loading = document.getElementById('loading');
    loading.classList.remove('hidden');
    
    const params = new URLSearchParams();
    
    // Add filters
    if (currentFilters.category) {
        params.append('category', currentFilters.category);
    }
    if (currentFilters.minPrice) {
        params.append('min_price', currentFilters.minPrice);
    }
    if (currentFilters.maxPrice) {
        params.append('max_price', currentFilters.maxPrice);
    }
    
    // Add sorting
    const sortBy = document.getElementById('sort-by').value;
    params.append('sort', sortBy);
    
    try {
        const res = await fetch(`/api/store/products?${params}`);
        currentProducts = await res.json();
        displayProducts(currentProducts);
    } catch (error) {
        console.error('Error loading products:', error);
        showNotification('Failed to load products', 'error');
    } finally {
        loading.classList.add('hidden');
    }
}

// Display products in grid
function displayProducts(products) {
    const container = document.getElementById('products-container');
    
    if (products.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center py-20 text-gray-600">No products found matching your criteria.</div>';
        return;
    }
    
    container.innerHTML = products.map(product => {
        const discount = product.original_price 
            ? Math.round((1 - product.price/product.original_price) * 100)
            : 0;
        
        return `
            <div class="product-card bg-white rounded-lg shadow-md overflow-hidden cursor-pointer" onclick="viewProduct('${product.id}')">
                <div class="relative">
                    <img 
                        src="${product.images[0] || '/static/store/placeholder.jpg'}" 
                        alt="${product.name}"
                        class="w-full h-48 object-cover"
                        onerror="this.src='/static/store/placeholder.jpg'"
                    />
                    ${discount > 0 ? `<div class="discount-badge">-${discount}%</div>` : ''}
                </div>
                
                <div class="p-4">
                    <h3 class="font-semibold text-lg mb-2 line-clamp-2">${product.name}</h3>
                    
                    <div class="mb-2">
                        ${product.original_price ? 
                            `<span class="text-gray-500 line-through text-sm">LKR ${product.original_price.toLocaleString()}</span>` 
                            : ''
                        }
                        <div class="text-blue-600 font-bold text-xl">LKR ${product.price.toLocaleString()}</div>
                    </div>
                    
                    <div class="flex items-center gap-1 mb-3">
                        <span class="text-yellow-500">${'★'.repeat(Math.floor(product.rating))}</span>
                        <span class="text-gray-400">${'★'.repeat(5 - Math.floor(product.rating))}</span>
                        <span class="text-sm text-gray-600">(${product.reviews_count})</span>
                    </div>
                    
                    <button 
                        onclick="event.stopPropagation(); addToCart('${product.id}')"
                        class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Add to Cart
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// View product details (simplified - can be enhanced with modal)
function viewProduct(productId) {
    const product = currentProducts.find(p => p.id === productId);
    if (!product) return;
    
    // Simple alert for now - can be replaced with a modal
    alert(`${product.name}\n\nPrice: LKR ${product.price.toLocaleString()}\n\n${product.description}\n\nFeatures:\n${product.features.join('\n')}`);
}

// Cart management
function addToCart(productId) {
    const product = currentProducts.find(p => p.id === productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: product.name,
            price: product.price,
            image: product.images[0],
            quantity: 1
        });
    }
    
    updateCart();
    showNotification(`${product.name} added to cart!`, 'success');
}

function updateCart() {
    updateCartCount();
    updateCartModal();
}

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    document.getElementById('cart-count').textContent = count;
}

function viewCart() {
    document.getElementById('cart-modal').classList.remove('hidden');
    updateCartModal();
}

function closeCart() {
    document.getElementById('cart-modal').classList.add('hidden');
}

function updateCartModal() {
    const container = document.getElementById('cart-items');
    const total = document.getElementById('cart-total');
    
    if (cart.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-600 py-8">Your cart is empty</p>';
        total.textContent = '0';
        return;
    }
    
    container.innerHTML = cart.map(item => `
        <div class="flex items-center gap-4 mb-4 pb-4 border-b">
            <img src="${item.image}" alt="${item.name}" class="w-20 h-20 object-cover rounded">
            <div class="flex-1">
                <h4 class="font-semibold">${item.name}</h4>
                <div class="text-blue-600 font-bold">LKR ${item.price.toLocaleString()}</div>
            </div>
            <div class="flex items-center gap-2">
                <button 
                    onclick="updateQuantity('${item.id}', -1)"
                    class="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
                >-</button>
                <span class="font-semibold">${item.quantity}</span>
                <button 
                    onclick="updateQuantity('${item.id}', 1)"
                    class="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
                >+</button>
                <button 
                    onclick="removeFromCart('${item.id}')"
                    class="text-red-600 hover:text-red-800 ml-2"
                >Remove</button>
            </div>
        </div>
    `).join('');
    
    const cartTotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    total.textContent = cartTotal.toLocaleString();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            updateCart();
        }
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

async function checkout() {
    if (cart.length === 0) {
        showNotification('Your cart is empty', 'error');
        return;
    }
    
    showCheckoutForm();
}

async function processPayHerePayment(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Processing...';
    
    try {
        // 1. Generate unique order ID
        const orderId = `ORD${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        // 2. Prepare items description
        const itemsDescription = cart.map(item => 
            `${item.name} x${item.quantity}`
        ).join(', ').substring(0, 255);
        
        // 3. Call backend to initiate payment
        const response = await fetch('/api/store/payment/initiate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                order_id: orderId,
                amount: total,
                items: cart,
                items_description: itemsDescription,
                customer_info: {
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    address: formData.get('address'),
                    city: formData.get('city'),
                    country: formData.get('country')
                }
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // 4. Create hidden form to submit to PayHere
            const paymentForm = document.createElement('form');
            paymentForm.method = 'POST';
            paymentForm.action = result.payment_url;
            paymentForm.style.display = 'none';
            
            // Add all payment data as hidden inputs
            for (const [key, value] of Object.entries(result.payment_data)) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = key;
                input.value = value;
                paymentForm.appendChild(input);
            }
            
            document.body.appendChild(paymentForm);
            
            // 5. Submit form (redirects to PayHere)
            paymentForm.submit();
            
        } else {
            throw new Error(result.error || 'Payment initiation failed');
        }
        
    } catch (error) {
        console.error('Payment error:', error);
        showNotification('Payment failed: ' + error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Filter functions
function applyFilters() {
    const categoryCheckboxes = document.querySelectorAll('input[name="category"]:checked');
    const priceRange = document.getElementById('price-range');
    
    currentFilters = {
        category: Array.from(categoryCheckboxes).map(cb => cb.value).join(','),
        minPrice: 0,
        maxPrice: parseInt(priceRange.value)
    };
    
    loadProducts();
}

function clearFilters() {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.getElementById('price-range').value = 500000;
    updatePriceDisplay();
    currentFilters = {};
    loadProducts();
}

// Price range display
const priceRange = document.getElementById('price-range');
if (priceRange) {
    priceRange.addEventListener('input', updatePriceDisplay);
}

function updatePriceDisplay() {
    const range = document.getElementById('price-range');
    const maxPrice = document.getElementById('max-price');
    if (range && maxPrice) {
        maxPrice.textContent = parseInt(range.value).toLocaleString();
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function getUserId() {
    // This should get the user ID from your session/cookie
    // For now, return null if not logged in
    // You can implement this based on your auth system
    return null; // Replace with actual implementation
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initStore);
